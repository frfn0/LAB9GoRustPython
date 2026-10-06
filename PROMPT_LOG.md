# Лог промптов — Лабораторная работа №9

**Студент:** Сурков Всеволод Сергеевич
**Группа:** 220032-11
**Вариант:** №2

Здесь фиксируются только промпты, относящиеся к лабораторной работе №9.

---

## Задание 2 (Go): горутина для фоновой обработки запросов

### Промпт 1. Постановка задачи

> смотри, что нужно сделать: лабораторные работы, методички в папке metodichki_tech,
> вариант 2, задания по варианту в методичке, кроме 10,11 лабораторных...
> в корне репозитория должен быть readme.md - инструкция к его созданию
> прописана в файле how_to_readme и файл PROMPT_LOG.md с логами промптов

### Промпт 2. Выбор объёма и репозиториев

> Объём заданий: только средние для всех лабораторных.
> Названия репозиториев: LAB9GoRustPython, LAB12AIAssisted, LAB13MultiAgent,
> а также LAB14 в таком же ключе.

### Промпт 3. Порядок работы

> сначала репозиторий и каркас

### Промпт 4. Способ реализации задания 2

> ка как в методичке

Ответ на уточнение о реализации: без собственной очереди задач и `202 Accepted`
на каждый запрос — ближе к формулировке методички.

### Промпт 5. Проверка результата

> ну чё там

### Реализация

Создан Go-сервис `go-service/main.go` на стандартной библиотеке:

- `POST /process` — принимает `{"numbers":[...]}`, отвечает сразу и передаёт
  вычисление в горутину;
- `GET /stats` — состояние фоновой обработки;
- `sync.WaitGroup` для ожидания горутин, `atomic.Int64` для счётчиков,
  `sync.Mutex` для результата последней задачи;
- `signal.NotifyContext` — graceful shutdown по Ctrl+C и SIGTERM.

### Проверка

`go vet ./go-service` и `go build ./go-service` — без ошибок, `gofmt` чистый.
Фактический вывод: пять запросов, пять фоновых горутин, `processed_jobs: 5`,
корректные суммы квадратов, код возврата при остановке — 0.

Результат: [go-service/result.txt](go-service/result.txt)

---

## Задание 4 (Go): передача данных из Python в Go через JSON

### Промпт

> го

Согласование перехода к заданию 4 после задания 2.

### Реализация

- `go-calculator/main.go` — Go-бинарь на стандартной библиотеке: читает один
  JSON-объект из stdin, возвращает в stdout `count`, `sum`, `sum_of_squares`
  и переданную метку обратно; ошибки — в stderr с кодом 1;
- `python/calculator_client.py` — клиент: `subprocess.run` с `text=True` и
  `encoding="utf-8"`, ошибки Go превращаются в `CalculatorError`;
- `python/demo_task4.py` — демонстрация, включая ошибочный случай;
- `tests/test_calculator.py` + `pytest.ini` — 6 тестов, покрытие клиента 90%.

### Проверка

`go vet ./go-calculator` и `go build` — без ошибок, `gofmt` чистый.
`python -m pytest tests -v --cov=calculator_client` — 6 passed, 90%.
Кириллица в поле `label` корректно проходит туда и обратно.

Результат: [go-calculator/result.txt](go-calculator/result.txt)

---

## Задание 7 (Rust): Python-модуль на Rust через PyO3

### Промпт

> летс гоу

Ответ на вопрос об установке `maturin`: ставить глобально и делать задание.

### Реализация

- `rust-fastmath/src/lib.rs` — модуль `fastmath` с функциями `sum_squares`,
  `mean`, `isqrt`; ошибки через `PyValueError` с текстом на русском;
- `rust-fastmath/Cargo.toml` — `crate-type = ["cdylib", "rlib"]` и
  `pyo3 = { version = "0.27", features = ["extension-module"] }`;
- `rust-fastmath/pyproject.toml` — build-backend `maturin`,
  `[tool.maturin] features = ["pyo3/extension-module"]`;
- `python/demo_task7.py` — демонстрация вызовов, ошибок и сравнения с Python;
- `tests/test_fastmath.py` — 14 тестов, `importorskip` с инструкцией по сборке.

### Первая неудачная попытка

`signal.Notify` из задания 2 не сработал на Windows: `CTRL_C_EVENT` нельзя
адресовать конкретной группе процессов. Решение — `signal.NotifyContext` без
списка сигналов. Это не ошибка ИИ, а особенность Windows, которую пришлось
учесть при первой же проверке.

### Проверка

- `cargo build` — успешно, 25.05s
- `python -m maturin build --release` — wheel `fastmath-0.1.0-cp310-cp310-win_amd64.whl`
- `pip install --force-reinstall` — установлено, `import fastmath` работает
- `python -m pytest tests -v` — 20 passed
- Сравнение с Python на 2 000 000 чисел: Rust 0.0200 сек против Python
  0.1324 сек, ускорение 6.6x, результаты совпали

Результат: [rust-fastmath/result.txt](rust-fastmath/result.txt)