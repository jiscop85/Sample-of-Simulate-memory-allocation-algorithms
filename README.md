# شبیه‌سازی الگوریتم‌های تخصیص حافظه

پروژه‌ای برای بررسی **First Fit**، **Best Fit** و **Worst Fit** در تخصیص حافظه ثابت (Fixed Partition) به پردازه‌ها و تحلیل **Internal Fragmentation**.

---

## اجرا روی سیستم جدید (ساده‌ترین روش)

### ویندوز — یک کلیک (پیشنهادی)

**دوبار کلیک روی `INSTALL_AND_RUN.bat`** — نصب + اجرای GUI

### ویندوز — دو مرحله

| مرحله | فایل | توضیح |
|-------|------|--------|
| **۱ (بار اول)** | `setup.bat` | نصب خودکار Python libs + ساخت `.venv` |
| **۲ (هر بار)** | `start.bat` | باز کردن GUI |

> فایل `راهنمای_سریع.txt` را هم بخوانید.

### پیش‌نیاز
- **Python 3.8+** از [python.org](https://www.python.org/downloads/)
- هنگام نصب: تیک **Add Python to PATH** را بزنید

### انتقال به سیستم دیگر
1. کل پوشه پروژه را کپی کنید (فلش، ZIP، ...)
2. پوشه `.venv` را **کپی نکنید** (روی سیستم جدید خودکار ساخته می‌شود)
3. روی سیستم جدید `setup.bat` را اجرا کنید

**ساخت ZIP آماده:** دوبار کلیک روی `pack_for_transfer.bat`

### لینوکس / مک
```bash
chmod +x setup.sh start.sh
./setup.sh    # بار اول
./start.sh    # هر بار
```

### روش جایگزین (همه OS)
```bash
python setup_project.py install --run
```

---

## رابط گرافیکی (GUI)

```bash
start.bat          # ویندوز
./start.sh         # لینوکس/مک
python main.py --gui
```

**قابلیت‌های GUI:**
- طراحی مدرن Dark Theme با CustomTkinter
- ورود دستی + نمونه‌های آماده + بارگذاری JSON
- تب جداگانه برای هر الگوریتم
- نقشه حافظه + نمودار + مقایسه
- ذخیره گزارش و خروجی PNG
- میانبر: `Ctrl + Enter`

---

## حالت خط فرمان (CLI)

```bash
start_cli.bat      # منوی تعاملی
python main.py
python main.py --sample classic --no-interactive
```

---

## نمونه‌های آماده

| نام | توضیح |
|-----|--------|
| `classic` | مثال کلاسیک درسی |
| `balanced` | بلوک‌ها و پردازه‌های نزدیک به هم |
| `stress` | تست fragmentation بالا |
| `partial_fail` | برخی پردازه‌ها تخصیص نمی‌شوند |

---

## فایل‌های اجرایی

| فایل | کاربرد |
|------|--------|
| `INSTALL_AND_RUN.bat` | **نصب + اجرا در یک کلیک** |
| `setup.bat` | نصب خودکار (ویندوز) |
| `start.bat` | اجرای GUI (ویندوز) |
| `start_cli.bat` | اجرای CLI (ویندوز) |
| `pack_for_transfer.bat` | ساخت ZIP قابل انتقال |
| `setup_project.py` | نصب/اجرا (کراس‌پلتفرم) |
| `setup.sh` / `start.sh` | لینوکس و مک |

---

## تست و بررسی کامل پروژه

```bash
python verify_project.py    # تست + شبیه‌سازی + بررسی فایل‌ها
python -m unittest tests.test_simulator -v
```

## مستندات تحویلی

| فایل | توضیح |
|------|--------|
| `docs/گزارش_پروژه.md` | گزارش کامل فارسی (Markdown) |
| `docs/گزارش_پروژه.html` | گزارش قابل چاپ — Ctrl+P → Save as PDF |
| `docs/ارائه_اسلاید.md` | ۱۰ اسلاید آماده ارائه |

---

## ساختار پروژه

```
memory_allocator/     # کد اصلی + GUI
samples/              # نمونه JSON
tests/                # تست واحد
output/               # خروجی‌های تولیدشده
main.py               # نقطه ورود
requirements.txt      # وابستگی‌ها
```

---

## فرمول‌ها

- **Internal Fragmentation** = Block Size − Process Size
- **Memory Utilization** = (Used Memory / Total Memory) × 100

## نتیجه نمونه classic

| الگوریتم | تخصیص | Fragmentation | Utilization |
|----------|-------|---------------|-------------|
| First Fit | 3/4 | 559 KB | 43.59% |
| **Best Fit** | **4/4** | **433 KB** | **68.65%** |
| Worst Fit | 3/4 | 659 KB | 43.59% |
