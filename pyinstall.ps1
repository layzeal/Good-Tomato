param
(
    [string]$v
)
python -m venv ./.env/
./.env\Scripts/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wxpython win10toast pyinstaller
./.env\Scripts/pyinstaller -F tomato.py --i c:/Start/git/Good-Tomato/tomato.ico -n "tomato v$v" --distpath "./dist/tomato v$v/" --specpath ./spec/ -w
cp ./tomato.ico "./dist/tomato v$v/tomato.ico"
cp ./config.json "./dist/tomato v$v/config.json"
Compress-Archive -Path "./dist/tomato v$v" -DestinationPath "./dist/tomato v$v.zip"