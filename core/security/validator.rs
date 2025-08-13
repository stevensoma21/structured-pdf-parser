// Configuration validation module
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};

#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationConfig {
    pub customer_id: String,
    pub features: Vec<String>,
    pub expires_at: DateTime<Utc>,
}

impl ValidationConfig {
    pub fn is_valid(&self) -> bool {
        Utc::now() < self.expires_at
    }
}
