#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import locale
import os
import platform
import string
import time
from pathlib import Path
from subprocess import PIPE, run

from tpl import *


def creat_py_venv():
    venv_dir = root_dir / '.venv'

    flags = True
    while True:
        os_platform = platform.system()
        if os_platform == 'Windows':
            base_python_path = 'python'
            venv_python_path = venv_dir / 'scripts' / 'python.exe'
            venv_pip_path = venv_dir / 'scripts' / 'pip.exe'

        if os_platform == 'Linux':
            base_python_path = 'python3'
            venv_python_path = venv_dir / 'bin' / 'python3'
            venv_pip_path = venv_dir / 'bin' / 'pip3'

        if not all([venv_python_path.exists(), venv_pip_path.exists()]):
            if flags:
                run(f'{base_python_path} -m venv .venv',
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE)
                flags = False

            else:
                raise ValueError(f'''failed to create python venv

the command maybe as follows:

windows:
cd {root_dir}
python -m venv .venv

linux:
cd {root_dir}
python3 -m venv .venv
''')
        else:
            break

    return venv_python_path, venv_pip_path


def pre():
    appname = root_dir.stem
    author = input('author: ')

    createdate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    description = input('description: ') or ''

    info = {
        'appname': appname,
        'author': author,
        'createdate': createdate,
        'description': description
    }

    system_encoding = locale.getpreferredencoding()
    vnev_python_path, venv_pip_path = creat_py_venv()

    cmd_list = (
        f'{venv_pip_path} install -i https://mirrors.aliyun.com/pypi/simple/ pip -U',
        f'{venv_pip_path} config set global.index-url https://mirrors.aliyun.com/pypi/simple/',
        f'{venv_pip_path} config set global.trusted-host mirrors.aliyun.com',
        f'{venv_pip_path} config set global.timeout 6000')
    for cmd in cmd_list:
        run(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    requirements_file = root_dir / 'requirements.txt'
    try:
        with open(requirements_file) as file:
            requirements = file.read()
    except:
        requirements = None

    if requirements:
        p = run(f'{venv_pip_path} list', shell=True, stdout=PIPE, stderr=PIPE)
        installed_packages = p.stdout.decode(system_encoding, errors='ignore')

        for line in requirements.split('\n'):
            try:
                package, ver = line.strip().split('==')
            except ValueError:
                continue

            if package not in installed_packages:
                run(f'{venv_pip_path} install {line}',
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE)
                print(f'install package: {package}')

        time.sleep(2)

    bin_dir = root_dir / 'bin'
    conf_dir = root_dir / 'conf'
    core_dir = root_dir / 'core'
    db_dir = root_dir / 'db'
    docs_dir = root_dir / 'docs'
    init_dir = root_dir / 'init'
    input_dir = root_dir / 'input'
    log_dir = root_dir / 'log'
    output_dir = root_dir / 'output'
    res_dir = root_dir / 'res'
    tests_dir = root_dir / 'tests'

    dir_tuple = (bin_dir, conf_dir, core_dir, db_dir, docs_dir, init_dir,
                 input_dir, log_dir, output_dir, res_dir, tests_dir)
    for _dir in dir_tuple:
        _dir.mkdir(exist_ok=True, parents=True)

    dirs_file = core_dir / 'dirs.py'
    gitignore_file = root_dir / '.gitignore'
    launch_file = core_dir / 'launch.py'
    log_file = core_dir / 'log.py'
    main_file = core_dir / 'main.py'
    readme_file = root_dir / 'README.md'
    start_file_cmd = root_dir / 'start.bat'
    start_file_dash = root_dir / 'start.sh'

    file_tuple = ((dirs_file, dirs_str), (gitignore_file, gitignore_str),
                  (launch_file, launch_str), (log_file, log_str),
                  (main_file, main_str), (readme_file, readme_str),
                  (start_file_cmd, start_str_cmd), (start_file_dash,
                                                    start_str_dash))
    for file in file_tuple:
        file_path, file_content = file
        if not file_path.exists():
            encoding = 'gbk' if file_path == start_file_cmd else 'utf-8'
            s = string.Template(file_content)
            s = s.safe_substitute(info)
            with open(file_path, 'w', encoding=encoding) as fp:
                fp.write(s)

    print('everything is ok, enjoy')


if __name__ == '__main__':
    pwd = Path(__file__).resolve()
    root_dir = pwd.parent.parent

    os.chdir(root_dir)
    pre()
