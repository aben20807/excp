# excp

Copy files with comparison checks.

I just add GUI for [`shutil.copy2`](https://docs.python.org/3/library/shutil.html?highlight=shutil%20copy2#shutil.copy2) and [`filecmp.cmp`](https://docs.python.org/3/library/filecmp.html?highlight=filecmp%20cmp#filecmp.cmp).

## Build from source

+ Python 3.9.13

+ Windows powershell commands:
```powershell
> python -m virtualenv venv
> .\venv\Scripts\Activate.ps1
> pip install alive-progress
> pip install pyinstaller
> pyinstaller -F -c --clean --collect-all grapheme --icon=excp.ico .\excp\excp.py
```

## Performance

Benchmark: 40 .jpg + 40 .nef (1.52 GB, 1,636,901,294 Bytes) from NAS to NAS locally

+ Copy by ctrl-c ctrl-v: 19s
+ Copy by excp: 49s
## Disclaimer

While the author uses excp to copy the files from his camera to the PC, you should not rely on this program for your important data. The author is not responsible for any damage to the data.

## Icon credit

+ The [icon (excp.ico)](https://icon-icons.com/icon/copy-paste-move-square/67897) is from [Kirill Kazachek](https://www.behance.net/kazachek) who shares it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)