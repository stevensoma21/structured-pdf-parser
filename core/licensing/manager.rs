// License management module
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct License {
    pub license_id: String,
    pub customer_id: String,
    pub features: Vec<String>,
    pub expires_at: DateTime<Utc>,
}

impl License {
    pub fn is_valid(&self) -> bool {
        Utc::now() < self.expires_at
    }
}
