"""Клиент Go-бинаря калькулятора: Python -> stdin -> Go -> stdout -> Python."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Sequence

# Корень репозитория: python/calculator_client.py -> ..
REPO_ROOT = Path(__file__).resolve().parent.parent
CALCULATOR_BINARY = REPO_ROOT / "go-calculator" / "calculator"


class CalculatorError(RuntimeError):
    """Ошибка, возвращённая Go-бинарником или самим запуском."""


def build_binary() -> Path:
    """Собирает Go-бинарь калькулятора и возвращает путь к исполняемому файлу."""
    subprocess.run(
        ["go", "build", "-o", str(CALCULATOR_BINARY), "./go-calculator"],
        cwd=REPO_ROOT,
        check=True,
    )
    return CALCULATOR_BINARY


def calculate(numbers: Sequence[int], label: str = "") -> dict[str, object]:
    """Передаёт числа в Go-бинарь через stdin и возвращает разобранный ответ.

    Raises:
        CalculatorError: если бинарь вернул ненулевой код или некорректный JSON.
    """
    payload = json.dumps({"label": label, "numbers": list(numbers)})

    completed = subprocess.run(
        [str(CALCULATOR_BINARY)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )

    if completed.returncode != 0:
        raise CalculatorError(
            f"калькулятор завершился с кодом {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )

    try:
        result: dict[str, object] = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CalculatorError(
            f"не удалось разобрать ответ калькулятора: {completed.stdout!r}"
        ) from exc

    return result