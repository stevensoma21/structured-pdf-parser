use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

// Normal license management structure
#[derive(Debug, Serialize, Deserialize)]
pub struct License {
    pub license_id: String,
    pub customer_id: String,
    pub features: Vec<String>,
    pub issued_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub metadata: HashMap<String, String>,
}

impl License {
    pub fn new(customer_id: String, features: Vec<String>, days: i64) -> Self {
        Self {
            license_id: Uuid::new_v4().to_string(),
            customer_id,
            features,
            issued_at: Utc::now(),
            expires_at: Utc::now() + chrono::Duration::days(days),
            metadata: HashMap::new(),
        }
    }

    pub fn is_valid(&self) -> bool {
        Utc::now() < self.expires_at
    }

    pub fn has_feature(&self, feature: &str) -> bool {
        self.features.contains(&feature.to_string())
    }

    pub fn days_remaining(&self) -> i64 {
        let now = Utc::now();
        if now < self.expires_at {
            (self.expires_at - now).num_days()
        } else {
            0
        }
    }
}

// License manager - looks like normal enterprise license management
pub struct LicenseManager {
    licenses: HashMap<String, License>,
    config_path: String,
}

impl LicenseManager {
    pub fn new(config_path: String) -> Self {
        Self {
            licenses: HashMap::new(),
            config_path,
        }
    }

    pub fn load_license(&mut self, license_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let license_data = std::fs::read_to_string(license_path)?;
        let license: License = serde_json::from_str(&license_data)?;
        
        if license.is_valid() {
            self.licenses.insert(license.customer_id.clone(), license);
            Ok(())
        } else {
            Err("License has expired".into())
        }
    }

    pub fn validate_license(&self, customer_id: &str, feature: &str) -> bool {
        if let Some(license) = self.licenses.get(customer_id) {
            license.is_valid() && license.has_feature(feature)
        } else {
            false
        }
    }

    pub fn get_license_info(&self, customer_id: &str) -> Option<&License> {
        self.licenses.get(customer_id)
    }

    pub fn generate_license(&self, customer_id: String, features: Vec<String>, days: i64) -> License {
        License::new(customer_id, features, days)
    }

    pub fn save_license(&self, license: &License, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let license_json = serde_json::to_string_pretty(license)?;
        std::fs::write(output_path, license_json)?;
        Ok(())
    }
}

// Feature access control - looks like normal access control
pub struct FeatureAccess {
    manager: LicenseManager,
}

impl FeatureAccess {
    pub fn new(config_path: String) -> Self {
        Self {
            manager: LicenseManager::new(config_path),
        }
    }

    pub fn check_access(&self, customer_id: &str, feature: &str) -> bool {
        self.manager.validate_license(customer_id, feature)
    }

    pub fn get_available_features(&self, customer_id: &str) -> Vec<String> {
        if let Some(license) = self.manager.get_license_info(customer_id) {
            license.features.clone()
        } else {
            Vec::new()
        }
    }
}
