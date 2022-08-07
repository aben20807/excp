import tkinter as tk
from tkinter import filedialog
from alive_progress import alive_bar
import shutil
import filecmp
import os, sys
import configparser


root = tk.Tk()
root.withdraw()

CONFIG = {"Settings": {"overwrite": True, "retry_max": 3, "close_after_done": False}}


def get_config_path():
    app_path = ""
    if getattr(sys, "frozen", False):
        app_path = os.path.dirname(sys.executable)
    elif __file__:
        app_path = os.path.dirname(__file__)
    config_path = os.path.join(app_path, "config.ini")
    return config_path


def read_config():
    config = configparser.ConfigParser()
    config.read(get_config_path(), encoding="utf-8-sig")
    CONFIG["Settings"]["overwrite"] = config.getboolean("Settings", "overwrite")
    CONFIG["Settings"]["retry_max"] = config.getint("Settings", "retry_max")
    CONFIG["Settings"]["close_after_done"] = config.getboolean(
        "Settings", "close_after_done"
    )


def gen_config():
    config = configparser.ConfigParser()
    config.read_dict(CONFIG)
    with open(get_config_path(), "w") as configfile:
        config.write(configfile)


class FileNotSameException(Exception):
    pass


class ReachRetryMaxException(Exception):
    pass


def main():

    file_paths = filedialog.askopenfilenames(parent=root, title="Choose a file")
    # print(root.tk.splitlist(file_paths))

    dirname = filedialog.askdirectory(parent=root, title="Choose a file")
    # print(root.tk.splitlist(dirname))

    retry_cnt = 0
    it = iter(file_paths)
    src_path, at_end = next(it, ""), object()
    with alive_bar(len(file_paths), dual_line=True, title="Copying...") as update:
        while src_path is not at_end:
            try:
                dst_path = os.path.join(dirname, os.path.basename(src_path))
                # If the target file is existing and overwrite is not allowed,
                # just show the message rather than copy the file
                if not os.path.exists(dst_path) or CONFIG["Settings"]["overwrite"]:
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
                update()
                src_path = next(it, at_end)

            except FileNotSameException as e:
                print(f"{e}. Retry...")
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                retry_cnt += 1
                if retry_cnt >= CONFIG["Settings"]["retry_max"]:
                    raise ReachRetryMaxException(
                        f"Reach maximum retries ({CONFIG['Settings']['retry_max']}) for {e}"
                    )
                continue


if __name__ == "__main__":
    if os.path.exists(get_config_path()):
        read_config()
    else:
        gen_config()

    try:
        print("Start copying...")
        main()
        print("Finish copying...")
        if not CONFIG["Settings"]["close_after_done"]:
            input("Press any key to leave")
    except Exception as e:
        print(e)
        sys.exit(1)
