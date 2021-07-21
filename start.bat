@echo off

cd /d %~dp0

set url_1="https://cdn.npm.taobao.org/dist/python/3.7.4/python-3.7.4.exe"
set url_2="https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe"

if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set python_dir=%LocalAppData%\Programs\Python37-32
) else (
    set python_dir=%LocalAppData%\Programs\Python37
)

set temp_file=%Temp%\python-3.7.4.exe

if not exist .venv\scripts\python.exe (
    python -m venv .venv 1>nul 2>nul

    if not exist .venv\scripts\python.exe (
        certutil -urlcache -split -f %url_1% %temp_file% 1>nul 2>nul

        if %errorlevel% NEQ 0 (
            certutil -urlcache -split -f %url_2% %temp_file% 1>nul 2>nul

            if %errorlevel% NEQ 0 (
                echo Error: failed to download python, check the network!
                pause >nul
                exit
            )
        )

        %temp_file% /passive /quiet TargetDir=%python_dir%
        %python_dir%\python.exe -m venv .venv 1>nul 2>nul
    )
)

.venv\scripts\python.exe core\launch.py