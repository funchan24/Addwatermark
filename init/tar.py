#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import platform
import shutil
import tempfile
import time
from distutils.core import setup
from pathlib import Path
from subprocess import PIPE, run
from zipfile import ZipFile


def pack_pyd(cur_dir, excepts=('launch.py')):
    while True:
        try:
            from Cython.Build import cythonize
            break
        except ImportError:
            run('pip install cython', shell=True, stdout=PIPE, stderr=PIPE)
            time.sleep(5)

    build_dir_list = set()
    temp_dir_list = set()
    temp_file_list = set()

    for file in cur_dir.rglob('*.py'):
        if file.name not in excepts:
            _file = str(file)
            build_dir = file.parent
            _build_dir = str(build_dir)
            build_temp_dir = build_dir / 'temp'
            _build_temp_dir = str(build_temp_dir)

            try:
                setup(ext_modules=cythonize([_file]),
                      script_args=[
                          "build_ext", "-b", _build_dir, "-t", _build_temp_dir
                      ])

                build_dir_list.add(build_dir)
                temp_file_list.add(file)
                temp_file_list.add(file.with_suffix('.c'))
                temp_dir_list.add(build_temp_dir)

            except Exception as e:
                print(f'error occurred during pack {file}, message: {e}')

    for build_dir in build_dir_list:
        for file in build_dir.iterdir():
            if file.suffix in ('.pyd', '.so'):
                name_list = file.name.split('.')
                new_name = file.with_name(f'{name_list[0]}.{name_list[-1]}')
                file.rename(new_name)

    for temp_dir in temp_dir_list:
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(e)
            pass

    for temp_file in temp_file_list:
        try:
            temp_file.unlink()
        except Exception as e:
            print(e)


def tar():
    temp_dir = Path(tempfile.mkdtemp())
    for file in root_dir.iterdir():
        if file.name not in ('.git', '.venv', '.vscode', 'db', 'input', 'log',
                             'output'):
            src = file
            dst = temp_dir / file.name
            if file.is_file():
                shutil.copy(src, dst)
            else:
                shutil.copytree(src, dst)

    db_dir = temp_dir / 'db'
    input_dir = temp_dir / 'input'
    log_dir = temp_dir / 'log'
    output_dir = temp_dir / 'output'
    dirs = (db_dir, input_dir, log_dir, output_dir)
    for _dir in dirs:
        _dir.mkdir(parents=True, exist_ok=True)

    app_path = root_dir / (root_dir.name + '.zip')
    with ZipFile(app_path, 'w') as z_file:
        for file in temp_dir.rglob('*'):
            if '__pycache__' not in str(file):
                z_file.write(file, file.relative_to(temp_dir))

    os_platform = platform.system()
    if os_platform == 'Windows':
        run(f'EXPLORER {root_dir}', shell=True, stdout=PIPE, stderr=PIPE)


if __name__ == '__main__':
    pwd = Path(__file__).resolve()
    root_dir = pwd.parent.parent
    core_dir = root_dir / 'core'

    # pack_pyd(core_dir)
    tar()
