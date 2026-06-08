#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo ""
echo "  ============================================================"
echo "    نصب خودکار - شبیه‌سازی تخصیص حافظه"
echo "  ============================================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "  [خطا] python3 نصب نیست."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "  [1/4] $(python3 --version)"

if [ ! -d ".venv" ]; then
    echo "  [2/4] ساخت محیط مجازی..."
    python3 -m venv .venv
else
    echo "  [2/4] محیط مجازی از قبل وجود دارد."
fi

echo "  [3/4] نصب کتابخانه‌ها..."
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt

echo "  [4/4] اجرای تست‌ها..."
python -m unittest tests.test_simulator -q

echo ""
echo "  نصب تمام شد! برای اجرا: ./start.sh"
echo ""
