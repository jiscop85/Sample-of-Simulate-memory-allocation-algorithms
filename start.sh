#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "محیط مجازی یافت نشد. در حال نصب..."
    bash setup.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python main.py --gui
