"""Демонстрация задания 4: Python передаёт данные в Go через JSON."""

from __future__ import annotations

from calculator_client import CalculatorError, build_binary, calculate


def main() -> None:
    print(f"Go-бинарь: {build_binary()}")
    print()

    print("Пример из методички: [1, 2, 3, 4, 5]")
    print(f"  ответ Go: {calculate([1, 2, 3, 4, 5])}")

    print()
    print("Структура с меткой, чтобы видеть обмен полями туда и обратно:")
    result = calculate([10, 20, 30], label="отчёт за неделю")
    print(f"  ответ Go: {result}")
    print(f"  метка вернулась из Go без изменений: {result['label']!r}")

    print()
    print("Отрицательные числа:")
    print(f"  ответ Go: {calculate([-4, 5], label='смешанные')}")

    print()
    print("Обработка ошибки: пустой массив чисел")
    try:
        calculate([])
    except CalculatorError as exc:
        print(f"  поймано ожидаемое исключение: {exc}")


if __name__ == "__main__":
    main()