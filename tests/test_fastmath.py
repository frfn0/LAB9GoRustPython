"""Тесты Python-модуля fastmath, собранного на Rust через PyO3."""

from __future__ import annotations

import pytest

fastmath = pytest.importorskip(
    "fastmath",
    reason=(
        "модуль fastmath не собран. Выполни в каталоге rust-fastmath: "
        "python -m maturin build --release, затем "
        "pip install --force-reinstall target/wheels/fastmath-*.whl"
    ),
)


def test_модуль_экспортирует_три_функции() -> None:
    exported = {name for name in dir(fastmath) if not name.startswith("_")}
    assert {"sum_squares", "mean", "isqrt"} <= exported


def test_сумма_квадратов() -> None:
    assert fastmath.sum_squares([1, 2, 3, 4, 5]) == 55


def test_сумма_квадратов_пустого_списка() -> None:
    assert fastmath.sum_squares([]) == 0


def test_сумма_квадратов_отрицательных_чисел() -> None:
    assert fastmath.sum_squares([-3, 4]) == 25


def test_среднее() -> None:
    assert fastmath.mean([1, 2, 3, 4]) == 2.5


def test_среднее_пустого_списка_ошибка() -> None:
    with pytest.raises(ValueError, match="не должен быть пустым"):
        fastmath.mean([])


@pytest.mark.parametrize(
    ("number", "expected"),
    [(0, 0), (1, 1), (15, 3), (16, 4), (17, 4), (10**12, 10**6)],
)
def test_целочисленный_корень(number: int, expected: int) -> None:
    assert fastmath.isqrt(number) == expected


def test_целочисленный_корень_отрицательного_числа_ошибка() -> None:
    with pytest.raises(ValueError, match="не должно быть отрицательным"):
        fastmath.isqrt(-1)


def test_результат_совпадает_с_python() -> None:
    numbers = list(range(10_000))
    assert fastmath.sum_squares(numbers) == sum(n * n for n in numbers)