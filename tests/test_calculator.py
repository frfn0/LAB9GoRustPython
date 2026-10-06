"""Тесты клиента Go-бинаря калькулятора."""

from __future__ import annotations

import json
import subprocess

import pytest

from calculator_client import (
    CALCULATOR_BINARY,
    CalculatorError,
    build_binary,
    calculate,
)


@pytest.fixture(scope="module", autouse=True)
def _binary() -> None:
    build_binary()


def test_пример_из_методички() -> None:
    assert calculate([1, 2, 3, 4, 5]) == {
        "count": 5,
        "sum": 15,
        "sum_of_squares": 55,
    }


def test_метка_возвращается_из_go() -> None:
    result = calculate([10, 20, 30], label="отчёт за неделю")
    assert result["label"] == "отчёт за неделю"
    assert result["sum"] == 60
    assert result["sum_of_squares"] == 1400


def test_отрицательные_числа() -> None:
    assert calculate([-4, 5]) == {"count": 2, "sum": 1, "sum_of_squares": 41}


def test_пустой_массив_отклоняется_бинарём() -> None:
    with pytest.raises(CalculatorError):
        calculate([])


def test_неизвестное_поле_отклоняется() -> None:
    completed = subprocess.run(
        [str(CALCULATOR_BINARY)],
        input=json.dumps({"numbers": [1], "unexpected": True}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert completed.returncode == 1
    assert "не удалось разобрать JSON" in completed.stderr


def test_бинарь_не_печатает_лишнего_в_stdout() -> None:
    completed = subprocess.run(
        [str(CALCULATOR_BINARY)],
        input=json.dumps({"numbers": [7]}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert completed.returncode == 0
    assert json.loads(completed.stdout) == {
        "count": 1,
        "sum": 7,
        "sum_of_squares": 49,
    }