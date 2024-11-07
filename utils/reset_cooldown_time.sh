#!/bin/sh

current_dir=$(dirname "$(realpath $0)")
python_dir=$(dirname "$current_dir")

PYTHONPATH=$python_dir python3 $python_dir/utils/reset_cooldown_time.py -u $1 -p $2
