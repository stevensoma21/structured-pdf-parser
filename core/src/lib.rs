// Main library module - looks like normal Rust library structure
pub mod engine;
pub mod security;
pub mod licensing;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

// Re-export main components
pub use engine::extractor::*;
pub use security::validator::*;
pub use licensing::manager::*;

// Python module initialization
#[pymodule]
fn ml_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register engine functions
    m.add_function(wrap_pyfunction!(engine::extractor::initialize_engine, m)?)?;
    m.add_function(wrap_pyfunction!(engine::extractor::extract_modules, m)?)?;
    m.add_function(wrap_pyfunction!(engine::extractor::extract_steps, m)?)?;
    m.add_function(wrap_pyfunction!(engine::extractor::get_prompt, m)?)?;
    
    Ok(())
}
