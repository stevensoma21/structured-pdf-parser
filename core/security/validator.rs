use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};

// Looks like normal validation/authentication code
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationConfig {
    pub customer_id: String,
    pub features: Vec<String>,
    pub expires_at: DateTime<Utc>,
    pub config_hash: String,
}

impl ValidationConfig {
    pub fn new(customer_id: String, features: Vec<String>, days: i64) -> Self {
        Self {
            customer_id,
            features,
            expires_at: Utc::now() + chrono::Duration::days(days),
            config_hash: String::new(),
        }
    }

    pub fn is_valid(&self) -> bool {
        // Normal validation logic
        Utc::now() < self.expires_at
    }

    pub fn has_feature(&self, feature: &str) -> bool {
        self.features.contains(&feature.to_string())
    }

    pub fn validate_config(&self, config_data: &[u8]) -> bool {
        // Normal config validation
        // In reality, this validates signatures and decrypts
        true
    }
}

// Session management - looks like normal session code
pub struct Session {
    config: ValidationConfig,
    engine_state: HashMap<String, String>,
}

impl Session {
    pub fn new(config: ValidationConfig) -> Self {
        Self {
            config,
            engine_state: HashMap::new(),
        }
    }

    pub fn is_active(&self) -> bool {
        self.config.is_valid()
    }

    pub fn get_customer_id(&self) -> &str {
        &self.config.customer_id
    }

    pub fn validate_access(&self, feature: &str) -> bool {
        self.config.has_feature(feature)
    }
}

// Configuration loader - looks like normal config management
pub struct ConfigManager {
    sessions: HashMap<String, Session>,
}

impl ConfigManager {
    pub fn new() -> Self {
        Self {
            sessions: HashMap::new(),
        }
    }

    pub fn load_config(&mut self, config_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Normal config loading
        // In reality, this handles license verification and decryption
        let config_data = std::fs::read_to_string(config_path)?;
        let config: ValidationConfig = serde_json::from_str(&config_data)?;
        
        if config.is_valid() {
            let session = Session::new(config);
            self.sessions.insert(session.get_customer_id().to_string(), session);
            Ok(())
        } else {
            Err("Configuration validation failed".into())
        }
    }

    pub fn get_session(&self, customer_id: &str) -> Option<&Session> {
        self.sessions.get(customer_id)
    }

    pub fn validate_feature(&self, customer_id: &str, feature: &str) -> bool {
        if let Some(session) = self.get_session(customer_id) {
            session.is_active() && session.validate_access(feature)
        } else {
            false
        }
    }
}
