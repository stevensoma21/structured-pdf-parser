use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use cryptography::aead::{Aes256Gcm, Key, Nonce};
use cryptography::aead::generic_array::GenericArray;
use base64::{Engine as _, engine::general_purpose};
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use sha2::{Sha256, Digest};
use hmac::{Hmac, Mac};
use zeroize::Zeroize;
use std::collections::HashMap;

// Embedded encrypted payload (will be replaced during build)
const ENCRYPTED_PAYLOAD: &[u8] = include_bytes!("../assets/encrypted_payload.bin");

// License structure
#[derive(Debug, Serialize, Deserialize)]
struct License {
    customer_id: String,
    expiration: DateTime<Utc>,
    features: Vec<String>,
    hwid: Option<String>,
    wheel_hash: String,
    signature: String,
}

// Core extraction rules (encrypted)
#[derive(Debug, Serialize, Deserialize)]
struct ExtractionRules {
    module_patterns: Vec<String>,
    step_patterns: Vec<String>,
    flow_patterns: Vec<String>,
    taxonomy_patterns: Vec<String>,
    llm_prompts: HashMap<String, String>,
    confidence_thresholds: HashMap<String, f64>,
}

// Session state
struct Session {
    rules: Option<ExtractionRules>,
    customer_id: String,
    watermark: String,
}

impl Session {
    fn new() -> Self {
        Self {
            rules: None,
            customer_id: String::new(),
            watermark: String::new(),
        }
    }
}

// Global session (in production, this would be thread-local)
static mut SESSION: Option<Session> = None;

#[pyfunction]
fn initialize_core(license_path: &str) -> PyResult<bool> {
    unsafe {
        SESSION = Some(Session::new());
        
        // Load and verify license
        let license_data = std::fs::read_to_string(license_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(e.to_string()))?;
        
        let license: License = serde_json::from_str(&license_data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        
        // Check expiration
        if Utc::now() > license.expiration {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "License expired".to_string()
            ));
        }
        
        // Verify signature (simplified - in production use Ed25519)
        if !verify_license_signature(&license) {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Invalid license signature".to_string()
            ));
        }
        
        // Decrypt payload
        let session_key = derive_session_key(&license.customer_id);
        let rules = decrypt_payload(ENCRYPTED_PAYLOAD, &session_key)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        // Set session data
        if let Some(session) = &mut SESSION {
            session.rules = Some(rules);
            session.customer_id = license.customer_id;
            session.watermark = generate_watermark(&license.customer_id);
        }
        
        Ok(true)
    }
}

#[pyfunction]
fn extract_modules(text: &str) -> PyResult<Vec<HashMap<String, PyObject>>> {
    unsafe {
        let session = SESSION.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Core not initialized".to_string()
            ))?;
        
        let rules = session.rules.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Rules not loaded".to_string()
            ))?;
        
        // Apply extraction logic using decrypted rules
        let modules = apply_module_extraction(text, rules);
        
        // Add watermark
        let watermarked_modules = add_watermark(modules, &session.watermark);
        
        Ok(watermarked_modules)
    }
}

#[pyfunction]
fn extract_steps(text: &str) -> PyResult<Vec<HashMap<String, PyObject>>> {
    unsafe {
        let session = SESSION.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Core not initialized".to_string()
            ))?;
        
        let rules = session.rules.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Rules not loaded".to_string()
            ))?;
        
        // Apply extraction logic using decrypted rules
        let steps = apply_step_extraction(text, rules);
        
        // Add watermark
        let watermarked_steps = add_watermark(steps, &session.watermark);
        
        Ok(watermarked_steps)
    }
}

#[pyfunction]
fn get_llm_prompt(prompt_type: &str) -> PyResult<String> {
    unsafe {
        let session = SESSION.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Core not initialized".to_string()
            ))?;
        
        let rules = session.rules.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Rules not loaded".to_string()
            ))?;
        
        rules.llm_prompts.get(prompt_type)
            .cloned()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                format!("Unknown prompt type: {}", prompt_type)
            ))
    }
}

// Helper functions
fn verify_license_signature(license: &License) -> bool {
    // Simplified verification - in production use Ed25519
    let data = format!("{}:{}:{}", 
        license.customer_id, 
        license.expiration.to_rfc3339(),
        license.wheel_hash
    );
    
    let expected_hash = hex::encode(Sha256::digest(data.as_bytes()));
    license.signature == expected_hash
}

fn derive_session_key(customer_id: &str) -> [u8; 32] {
    let mut key = [0u8; 32];
    let mut hasher = Sha256::new();
    hasher.update(customer_id.as_bytes());
    hasher.update(b"codex_session_key_2024");
    key.copy_from_slice(&hasher.finalize());
    key
}

fn decrypt_payload(encrypted_data: &[u8], key: &[u8; 32]) -> Result<ExtractionRules, Box<dyn std::error::Error>> {
    // In production, this would use AES-GCM with proper nonce handling
    // For now, we'll use a simplified approach
    let cipher = Aes256Gcm::new(Key::from_slice(key));
    
    // Extract nonce and ciphertext (first 12 bytes are nonce)
    if encrypted_data.len() < 12 {
        return Err("Invalid encrypted data".into());
    }
    
    let nonce = Nonce::from_slice(&encrypted_data[..12]);
    let ciphertext = &encrypted_data[12..];
    
    let plaintext = cipher.decrypt(nonce, ciphertext)
        .map_err(|_| "Decryption failed")?;
    
    let rules: ExtractionRules = serde_json::from_slice(&plaintext)?;
    Ok(rules)
}

fn apply_module_extraction(text: &str, rules: &ExtractionRules) -> Vec<HashMap<String, PyObject>> {
    // Apply module extraction patterns from decrypted rules
    let mut modules = Vec::new();
    
    for pattern in &rules.module_patterns {
        // Simplified pattern matching - in production use regex
        if text.contains(pattern) {
            let mut module = HashMap::new();
            module.insert("pattern".to_string(), pattern.clone().into());
            module.insert("confidence".to_string(), 0.95f64.into());
            modules.push(module);
        }
    }
    
    modules
}

fn apply_step_extraction(text: &str, rules: &ExtractionRules) -> Vec<HashMap<String, PyObject>> {
    // Apply step extraction patterns from decrypted rules
    let mut steps = Vec::new();
    
    for pattern in &rules.step_patterns {
        // Simplified pattern matching - in production use regex
        if text.contains(pattern) {
            let mut step = HashMap::new();
            step.insert("pattern".to_string(), pattern.clone().into());
            step.insert("confidence".to_string(), 0.90f64.into());
            steps.push(step);
        }
    }
    
    steps
}

fn add_watermark<T>(items: Vec<T>, watermark: &str) -> Vec<T> {
    // Add watermark to outputs (simplified)
    items
}

fn generate_watermark(customer_id: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(customer_id.as_bytes());
    hasher.update(b"watermark_salt");
    format!("wm_{}", hex::encode(&hasher.finalize()[..8]))
}

#[pymodule]
fn codex_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(initialize_core, m)?)?;
    m.add_function(wrap_pyfunction!(extract_modules, m)?)?;
    m.add_function(wrap_pyfunction!(extract_steps, m)?)?;
    m.add_function(wrap_pyfunction!(get_llm_prompt, m)?)?;
    Ok(())
}
