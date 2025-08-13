// Main library module
pub mod engine;
pub mod security;
pub mod licensing;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pymodule]
fn ml_core(_py: Python, m: &PyModule) -> PyResult<()> {
    Ok(())
}
