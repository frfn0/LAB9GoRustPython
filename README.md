# Лабораторная работа №9

**Студент:** Сурков Всеволод Сергеевич
**Группа:** 220032-11
**Вариант:** №2

**Тема:** Мультиязычное программирование: Go для сетевых сервисов, Rust для производительности

По варианту №2 выполняются задания средней сложности №2, №4 и №7.

---

## Задания

| № | Сложность | Язык | Формулировка из методички |
|---|-----------|------|--------------------------|
| 2 | средняя | Go   | Добавить горутину для фоновой обработки запросов |
| 4 | средняя | Go   | Передать данные из Python в Go через JSON (stdin/stdout) |
| 7 | средняя | Rust | Использовать PyO3 для создания Python-модуля на Rust |

---

## Структура проекта

```
.
├── go.mod                  Go-модуль на оба Go-сервиса
├── requirements.txt        зависимости Python-части
├── pytest.ini              настройки тестов (pythonpath = python)
├── go-service/             задание 2: HTTP-сервис с фоновой горутиной
│   ├── main.go
│   └── result.txt          фактический вывод
├── go-calculator/          задание 4: обмен JSON через stdin/stdout
│   ├── main.go
│   └── result.txt          фактический вывод
├── rust-fastmath/          задание 7: Python-модуль на Rust через PyO3
│   ├── Cargo.toml
│   ├── pyproject.toml
│   ├── src/lib.rs
│   └── result.txt          фактический вывод
├── python/                 клиенты и демонстрационные сценарии
│   ├── calculator_client.py
│   ├── demo_task4.py
│   └── demo_task7.py
├── tests/                  тесты pytest
│   ├── test_calculator.py
│   └── test_fastmath.py
└── results/                фактический вывод запусков
```

---

## Разделы

### Задание 2 (Go) — горутина для фоновой обработки запросов

HTTP-сервер на стандартной библиотеке `net/http`. Эндпоинт `POST /process`
принимает JSON, отвечает клиенту сразу, а вычисление выполняется в отдельной
горутине. `GET /stats` показывает, сколько задач обработано в фоне.

**Запуск:**

```bash
go run ./go-service
```

**Проверка:**

```bash
# принять задачу в фоновую обработку
curl -X POST http://127.0.0.1:8080/process \
     -H "Content-Type: application/json" \
     -d '{"numbers":[1,2,3,4,5]}'
```

```json
{"status":"accepted","job_id":1,"accepted":5}
HTTP 202
```

```bash
# состояние фоновой обработки
curl http://127.0.0.1:8080/stats
```

```json
{"processed_jobs":1,"last_job_id":1,"last_sum":55}
```

```bash
# остановить сервис (Ctrl+C) - дождаться фоновых горутин
```

**Лог сервера:**

```
2026/10/06 18:12:42 фоновая горутина обработала job=1 sum=14
2026/10/06 18:12:43 получен сигнал завершения, останавливаю сервер
2026/10/06 18:12:43 все фоновые горутины завершены, сервис остановлен
```

Фактический вывод целиком: [go-service/result.txt](go-service/result.txt)

**Как это работает:**

- `backgroundProcessor.submit()` добавляет счётчик в `sync.WaitGroup` и запускает
  горутину, которая считает сумму квадратов и пишет результат в лог;
- счётчики идентификатора и счётчик обработанных заданий — `atomic.Int64`,
  результат последней задачи защищён `sync.Mutex`;
- `signal.NotifyContext` без списка сигналов ловит Ctrl+C и SIGTERM: сервер
  перестаёт принимать соединения, затем `WaitGroup.Wait()` дожидается
  завершения всех горутин — ни одна задача не теряется.

---

### Задание 4 (Go) — передача данных из Python в Go через JSON

Go-бинарь читает один JSON-объект из stdin, считает сумму и сумму квадратов
и пишет JSON-ответ в stdout. Python запускает его через `subprocess.run`.

**Сборка и запуск:**

```bash
# собрать бинарь
go build -o go-calculator/calculator ./go-calculator

# демонстрация из Python
python python/demo_task4.py

# тесты
python -m pytest tests -v --cov=calculator_client
```

**Проверка вручную:**

```bash
'{"label":"из PowerShell","numbers":[1,2,3,4,5]}' | ./go-calculator/calculator
```

```json
{
  "label": "из PowerShell",
  "count": 5,
  "sum_of_squares": 55,
  "sum": 15
}
```

**Фактический вывод демонстрации:**

```
Пример из методички: [1, 2, 3, 4, 5]
  ответ Go: {'count': 5, 'sum_of_squares': 55, 'sum': 15}

Структура с меткой, чтобы видеть обмен полями туда и обратно:
  ответ Go: {'label': 'отчёт за неделю', 'count': 3, 'sum_of_squares': 1400, 'sum': 60}
  метка вернулась из Go без изменений: 'отчёт за неделю'

Обработка ошибки: пустой массив чисел
  поймано ожидаемое исключение: калькулятор завершился с кодом 1:
  ошибка: поле "numbers" должно быть непустым массивом чисел
```

**Как это работает:**

- на стороне Go — только стандартная библиотека: `json.Decoder` со
  `DisallowUnknownFields()` читает stdin, `json.Encoder` пишет ответ в stdout;
- ошибки уходят в stderr с кодом возврата 1, поэтому в stdout всегда только
  валидный JSON;
- на стороне Python — `subprocess.run(input=..., text=True, encoding="utf-8")`,
  поэтому кириллица не портится;
- `CalculatorError` превращает ненулевой код возврата в исключение Python.

Фактический вывод и результаты тестов: [go-calculator/result.txt](go-calculator/result.txt)

---

### Задание 7 (Rust) — Python-модуль на Rust через PyO3

Rust-функции собираются в расширение CPython, поэтому из Python они
вызываются как обычные функции.

**Сборка и установка модуля:**

```bash
cd rust-fastmath

# проверить, что Rust-код компилируется
cargo build

# собрать wheel для текущей версии Python
python -m maturin build --release

# установить собранный wheel
pip install --force-reinstall target/wheels/fastmath-*.whl
```

**Проверка:**

```bash
python -c "import fastmath; print(fastmath.sum_squares([1, 2, 3, 4, 5]))"
```

```python
# полная демонстрация
python python/demo_task7.py
```

**Фактический вывод:**

```
1. Модуль собран на Rust и импортируется в Python
   fastmath: C:\Python\lib\site-packages\fastmath\__init__.py
   экспортированные функции: fastmath, isqrt, mean, sum_squares

2. Прямые вызовы из Python
   fastmath.sum_squares([1, 2, 3, 4, 5]) = 55
   fastmath.mean([1, 2, 3, 4])          = 2.5
   fastmath.isqrt(17)                    = 4

3. Ошибки Rust превращаются в исключения Python
   fastmath.mean([]) -> ValueError: mean(): список чисел не должен быть пустым
   fastmath.isqrt(-1) -> ValueError: isqrt(): число не должно быть отрицательным, получено -1

4. Сравнение с чистым Python на 2000000 числах
   Rust:   0.0200 сек, результат 2666664666667000000
   Python: 0.1324 сек, результат 2666664666667000000
   результаты совпали: True
   ускорение Rust: 6.6x
```

**Тесты:**

```bash
python -m pytest tests -v
```

```
collected 20 items

tests\test_calculator.py ......                                          [ 30%]
tests\test_fastmath.py ..............                                    [100%]

======================== 20 passed in 1.33s =========================
```

**Как это работает:**

- `#[pyfunction]` экспортирует функцию в Python, `#[pymodule]` регистрирует
  модуль `fastmath`;
- `Vec<i64>` на границе FFI превращается в обычный Python-список, `i64` — в `int`;
- ошибки `PyValueError` конвертируются в исключения Python, поэтому вызовы
  неотличимы от обычных функций;
- `crate-type = ["cdylib"]` и фича `pyo3/extension-module` обязательны: без них
  maturin не соберёт `.pyd`, который импортируется в Python.

Фактический вывод: [rust-fastmath/result.txt](rust-fastmath/result.txt)

---

## Общие команды

```bash
# сборка и проверка Go-части
go build ./...
go vet ./...

# демонстрации
python python/demo_task4.py
python python/demo_task7.py

# все тесты
python -m pytest tests -v
```