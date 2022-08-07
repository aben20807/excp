import asyncio
import tkinter as tk
from tkinter import filedialog
from alive_progress import alive_bar
import shutil
import filecmp
import os, sys
import configparser
import concurrent.futures


root = tk.Tk()
root.withdraw()

# default configuration for generation first time
CONFIG = {
    "Settings": {
        "overwrite": True,
        "retry_max": 3,
        "close_after_done": False,
        "thread_num": 8,
    }
}


def get_config_path():
    app_path = ""
    if getattr(sys, "frozen", False):
        app_path = os.path.dirname(sys.executable)
    elif __file__:
        app_path = os.path.dirname(__file__)
    config_path = os.path.join(app_path, "excp_config.ini")
    return config_path


def read_config():
    config = configparser.ConfigParser()
    config.read(get_config_path(), encoding="utf-8-sig")
    CONFIG["Settings"]["overwrite"] = config.getboolean("Settings", "overwrite")
    CONFIG["Settings"]["retry_max"] = config.getint("Settings", "retry_max")
    CONFIG["Settings"]["close_after_done"] = config.getboolean(
        "Settings", "close_after_done"
    )
    CONFIG["Settings"]["thread_num"] = config.getint("Settings", "thread_num")


def gen_config():
    config = configparser.ConfigParser()
    config.read_dict(CONFIG)
    with open(get_config_path(), "w") as configfile:
        config.write(configfile)


class FileNotSameException(Exception):
    pass


def open_dialogs():
    # Get file paths and target directory from dialog gui then return
    file_paths = filedialog.askopenfilenames(parent=root, title="Choose a file")
    dirname = filedialog.askdirectory(parent=root, title="Choose a file")
    return file_paths, dirname


def copy_task(file_paths, dirname, idx):
    retry_cnt = 0
    it = iter(file_paths)
    src_path, at_end = next(it, ""), object()
    with alive_bar(
        len(file_paths) * CONFIG["Settings"]["thread_num"],
        dual_line=True,
        title="Copying...",
        disable=(True if idx != 0 else False),
    ) as update:
        while src_path is not at_end:
            try:
                dst_path = os.path.join(dirname, os.path.basename(src_path))
                # If the target file is existing and overwrite is not allowed,
                # just show the message rather than copy the file
                if not os.path.exists(dst_path) or CONFIG["Settings"]["overwrite"]:
                    # Use copy2 to copy as more metadata as possible
                    shutil.copy2(src_path, dirname)
                    # Compare the file after it is copied
                    # If something different raise exception and retry
                    if not filecmp.cmp(src_path, dst_path, shallow=False):
                        raise FileNotSameException(
                            f"Files `{src_path}`, `{dst_path}` not the same"
                        )
                else:
                    print(f"File `{dst_path}` exists")

                # Reset the retry_cnt before go to the next
                retry_cnt = 0
                for _ in range(CONFIG["Settings"]["thread_num"]):
                    update()
                src_path = next(it, at_end)

            except FileNotSameException as e:
                print(f"{e}. Retry...")
                # Delete the file to retry the copy
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                retry_cnt += 1
                if retry_cnt >= CONFIG["Settings"]["retry_max"]:
                    # if still have error, skip this file and go throught the next one
                    print(
                        f"Reach maximum retries ({CONFIG['Settings']['retry_max']}) for {e}"
                    )
                    # Delete the broken file
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    # Reset the retry_cnt before go to the next
                    retry_cnt = 0
                    for _ in range(CONFIG["Settings"]["thread_num"]):
                        update()
                    src_path = next(it, at_end)
                    continue
                continue


def split_tasks(tasks, n):
    for i in range(0, len(tasks), n):
        yield tasks[i : i + n]


async def main(executor):
    file_paths, dirname = open_dialogs()

    if len(file_paths) == 0 or dirname == "":
        print(f"Files: {root.tk.splitlist(file_paths)}")
        print(f"Dir: {root.tk.splitlist(dirname)}")
        print("do nothing...")
        return

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(executor, copy_task, file_paths_sep, dirname, idx)
        for idx, file_paths_sep in enumerate(
            split_tasks(file_paths, len(file_paths) // CONFIG["Settings"]["thread_num"])
        )
    ]
    await asyncio.wait(tasks)


if __name__ == "__main__":
    if os.path.exists(get_config_path()):
        read_config()
    else:
        gen_config()

    print(f"Config: {CONFIG}")

    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=CONFIG["Settings"]["thread_num"],
    )

    print("Start copying...")
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main(executor))
    finally:
        event_loop.close()

    print("Finish copying...")
    if not CONFIG["Settings"]["close_after_done"]:
        input("Press enter to exit")
