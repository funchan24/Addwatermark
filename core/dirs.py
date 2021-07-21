#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

from pathlib import Path

pwd = Path(__file__).resolve()
root_dir = pwd.parent.parent
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
