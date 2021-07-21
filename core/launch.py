#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import locale
import os
import platform
import time
from pathlib import Path
from subprocess import PIPE, run


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
                print(f'create python venv')

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


def init(flags, *, module=None):
    system_encoding = locale.getpreferredencoding()
    venv_python_path, venv_pip_path = creat_py_venv()

    if flags == 0:
        cmd_list = (
            f'{venv_pip_path} install -i https://mirrors.aliyun.com/pypi/simple/ pip -U',
            f'{venv_pip_path} config set global.index-url https://mirrors.aliyun.com/pypi/simple/',
            f'{venv_pip_path} config set global.trusted-host mirrors.aliyun.com',
            f'{venv_pip_path} config set global.timeout 6000',
            f'{venv_pip_path} install chardet')
        for cmd in cmd_list:
            run(cmd, shell=True, stdout=PIPE, stderr=PIPE)

        from chardet import detect
        requirements_file = root_dir / 'requirements.txt'
        try:
            with open(requirements_file, 'rb') as file:
                content = file.read()
                file_encoding = detect(content)['encoding']
                requirements = content.decode(file_encoding, errors='ignore')
        except:
            requirements = None

        if requirements:
            p = run(f'{venv_pip_path} list',
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE)
            installed_packages = p.stdout.decode(system_encoding,
                                                 errors='ignore')

            for line in requirements.split('\n'):
                try:
                    package, _ver = line.strip().split('==')
                except ValueError:
                    continue

                if package not in installed_packages:
                    run(f'{venv_pip_path} install {line}',
                        shell=True,
                        stdout=PIPE,
                        stderr=PIPE)

                    print(f'install package: {package}')
                    time.sleep(1)

    else:
        if not module:
            raise ValueError('module name cannot be none')

        p = run(f'{venv_pip_path} install {module}',
                shell=True,
                stdout=PIPE,
                stderr=PIPE)

        if p.stderr:
            raise NotImplementedError(
                p.stderr.decode(system_encoding, errors='ignore'))

        print(f'install package: {module}')

        run(f'{venv_pip_path} freeze >requirements.txt',
            shell=True,
            stdout=PIPE,
            stderr=PIPE)


if __name__ == '__main__':
    pwd = Path(__file__).resolve()
    root_dir = pwd.parent.parent
    os.chdir(root_dir)

    flags = 0
    while True:
        try:
            from main import main
            main()
            break
        except ModuleNotFoundError as e:
            module = str(e).split("'")[-2]
            init(flags, module=module)
        finally:
            flags += 1
