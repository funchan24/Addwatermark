stty -echo

cd `dirname $0`

if [ ! -e ./.venv/bin/python3 ]; then
    python3 -m venv .venv
    if [ ! -e ./.venv/bin/python3 ]; then
        echo install python3 and run this script again
    fi
fi

./.venv/bin/python3 ./core/launch.py