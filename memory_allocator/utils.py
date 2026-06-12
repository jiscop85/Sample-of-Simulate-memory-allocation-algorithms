"""Input parsing and sample datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


SAMPLE_DATASETS: Dict[str, Dict[str, List[int]]] = {
    "classic": {
        "description": "مثال کلاسیک درسی (OS textbook)",
        "blocks": [100, 500, 200, 300, 600],
        "processes": [212, 417, 112, 426],
    },
    "balanced": {
        "description": "بلوک‌ها و پردازه‌های نزدیک به هم",
        "blocks": [300, 250, 400, 350, 200],
        "processes": [280, 240, 390, 180, 150],
    },
    "stress": {
        "description": "تست با fragmentation بالا",
        "blocks": [100, 100, 100, 100, 1000],
        "processes": [50, 50, 50, 50, 900, 80],
    },
    "partial_fail": {
        "description": "برخی پردازه‌ها تخصیص نمی‌شوند",
        "blocks": [200, 300, 150],
        "processes": [180, 250, 400, 100],
    },
}


def parse_int_list(text: str) -> List[int]:
    text = text.replace(",", " ").strip()
    if not text:
        return []

    values: List[int] = []
    for item in text.split():
        try:
            num = int(item)
        except ValueError as exc:
            raise ValueError(f"مقدار نامعتبر وارد شده است: {item}") from exc
        if num <= 0:
            raise ValueError("همه‌ی اعداد باید بزرگ‌تر از صفر باشند.")
        values.append(num)
    return values


def read_int_list(prompt: str) -> List[int]:
    while True:
        try:
            text = input(prompt).strip()
            values = parse_int_list(text)
            if not values:
                print("ورودی نباید خالی باشد. دوباره تلاش کن.")
                continue
            return values
        except ValueError as exc:
            print(f"خطا: {exc}")


def load_from_json(path: str) -> Tuple[List[int], List[int]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"فایل یافت نشد: {path}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    blocks = data.get("blocks")
    processes = data.get("processes")

    if not isinstance(blocks, list) or not isinstance(processes, list):
        raise ValueError("فایل JSON باید شامل کلیدهای 'blocks' و 'processes' باشد.")

    return [int(b) for b in blocks], [int(p) for p in processes]


def list_sample_names() -> List[str]:
    return list(SAMPLE_DATASETS.keys())
