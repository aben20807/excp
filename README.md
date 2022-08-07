
+ Windows powershell
```
python -m virtualenv venv
.\venv\Scripts\Activate.ps1
pip install alive-progress
pip install pyinstaller
pyinstaller -F -c --clean --collect-all grapheme --icon=excp.ico .\excp\excp.py
```

## Icon credit

+ The [icon](https://icon-icons.com/icon/copy-paste-move-square/67897) is from [Kirill Kazachek](https://www.behance.net/kazachek) who shares it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)