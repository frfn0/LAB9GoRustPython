"""Демонстрация задания 7: вызов функций Rust из Python через PyO3."""

from __future__ import annotations

import time
from pathlib import Path

BENCHMARK_SIZE = 2_000_000


def show_api() -> None:
    import fastmath

    print("1. Модуль собран на Rust и импортируется в Python")
    print(f"   fastmath: {fastmath.__file__}")
    exported = [name for name in dir(fastmath) if not name.startswith("_")]
    print(f"   экспортированные функции: {', '.join(exported)}")
    print()


def show_calls() -> None:
    import fastmath

    print("2. Прямые вызовы из Python")
    print(f"   fastmath.sum_squares([1, 2, 3, 4, 5]) = {fastmath.sum_squares([1, 2, 3, 4, 5])}")
    print(f"   fastmath.mean([1, 2, 3, 4])          = {fastmath.mean([1, 2, 3, 4])}")
    print(f"   fastmath.isqrt(17)                    = {fastmath.isqrt(17)}")
    print()


def show_errors() -> None:
    import fastmath

    print("3. Ошибки Rust превращаются в исключения Python")
    for call in ("fastmath.mean([])", "fastmath.isqrt(-1)"):
        try:
            eval(call)  # noqa: S307 - строковый вызов нужен только для наглядности
        except Exception as exc:
            print(f"   {call} -> {type(exc).__name__}: {exc}")
    print()


def show_benchmark() -> None:
    import fastmath

    print(f"4. Сравнение с чистым Python на {BENCHMARK_SIZE} числах")
    numbers = list(range(BENCHMARK_SIZE))

    start = time.perf_counter()
    rust_result = fastmath.sum_squares(numbers)
    rust_time = time.perf_counter() - start

    start = time.perf_counter()
    python_result = sum(x * x for x in numbers)
    python_time = time.perf_counter() - start

    print(f"   Rust:   {rust_time:.4f} сек, результат {rust_result}")
    print(f"   Python: {python_time:.4f} сек, результат {python_result}")
    print(f"   результаты совпали: {rust_result == python_result}")
    print(f"   ускорение Rust: {python_time / rust_time:.1f}x")


def main() -> None:
    print(f"Сборка модуля: {Path(__file__).resolve().parent.parent / 'rust-fastmath'}")
    print()
    show_api()
    show_calls()
    show_errors()
    show_benchmark()


if __name__ == "__main__":
    main()