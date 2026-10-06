//! Задание 7. Python-модуль на Rust через PyO3.
//!
//! Модуль `fastmath` собирается в расширение CPython, поэтому функции из
//! Rust вызываются из Python как обычные: `fastmath.sum_squares([1, 2, 3])`.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Возвращает сумму квадратов чисел.
///
/// `fastmath.sum_squares([1, 2, 3, 4, 5])` -> `55`
#[pyfunction]
fn sum_squares(numbers: Vec<i64>) -> i64 {
    numbers.iter().map(|n| n * n).sum()
}

/// Возвращает среднее арифметическое чисел.
///
/// # Errors
///
/// Возвращает `ValueError`, если передан пустой список.
#[pyfunction]
fn mean(numbers: Vec<f64>) -> PyResult<f64> {
    if numbers.is_empty() {
        return Err(PyValueError::new_err(
            "mean(): список чисел не должен быть пустым",
        ));
    }

    let total: f64 = numbers.iter().sum();
    Ok(total / numbers.len() as f64)
}

/// Возвращает целочисленный квадратный корень числа.
///
/// `fastmath.isqrt(17)` -> `4`
///
/// # Errors
///
/// Возвращает `ValueError`, если число отрицательное.
#[pyfunction]
fn isqrt(number: i64) -> PyResult<u64> {
    if number < 0 {
        return Err(PyValueError::new_err(format!(
            "isqrt(): число не должно быть отрицательным, получено {number}"
        )));
    }

    Ok((number as f64).sqrt() as u64)
}

/// Модуль `fastmath`, доступный в Python как `import fastmath`.
#[pymodule]
fn fastmath(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_squares, m)?)?;
    m.add_function(wrap_pyfunction!(mean, m)?)?;
    m.add_function(wrap_pyfunction!(isqrt, m)?)?;
    Ok(())
}
