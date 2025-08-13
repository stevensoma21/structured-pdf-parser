use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

// Import secure validation from security module
use crate::security::validator::{ValidationConfig, ConfigManager};

// Hardcoded security constants
const BUILD_TIMESTAMP: u64 = 1734123456; // Must match security module
const HARDCODED_EXPIRATION_DAYS: u64 = 14; // Must match security module

// Secure license structure with hardcoded expiration
#[derive(Debug, Serialize, Deserialize)]
pub struct License {
    pub license_id: String,
    pub customer_id: String,
    pub features: Vec<String>,
    pub issued_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub metadata: HashMap<String, String>,
    pub security_signature: String,
}

impl License {
    pub fn new(customer_id: String, features: Vec<String>) -> Self {
        // Use hardcoded build timestamp for consistent expiration
        let build_date = DateTime::from_timestamp(BUILD_TIMESTAMP as i64, 0)
            .unwrap_or_else(|| Utc::now());
        let expiration = build_date + chrono::Duration::days(HARDCODED_EXPIRATION_DAYS as i64);
        
        // Generate security signature
        let signature = Self::generate_security_signature(&customer_id, &build_date);
        
        Self {
            license_id: Uuid::new_v4().to_string(),
            customer_id,
            features,
            issued_at: build_date,
            expires_at: expiration,
            metadata: HashMap::new(),
            security_signature: signature,
        }
    }

    pub fn is_valid(&self) -> bool {
        // Use secure validation from security module
        let validation_config = ValidationConfig::new(
            self.customer_id.clone(),
            self.features.clone()
        );
        
        validation_config.is_valid()
    }

    pub fn has_feature(&self, feature: &str) -> bool {
        self.features.contains(&feature.to_string())
    }

    pub fn days_remaining(&self) -> i64 {
        let validation_config = ValidationConfig::new(
            self.customer_id.clone(),
            self.features.clone()
        );
        
        validation_config.days_remaining()
    }

    fn generate_security_signature(customer_id: &str, build_date: &DateTime<Utc>) -> String {
        // Use same signature generation as security module
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        const SECURITY_SALT: &str = "ml_core_2024_secure";
        
        let mut hasher = DefaultHasher::new();
        customer_id.hash(&mut hasher);
        build_date.timestamp().hash(&mut hasher);
        SECURITY_SALT.hash(&mut hasher);
        
        format!("{:x}", hasher.finish())
    }

    pub fn validate_signature(&self) -> bool {
        let build_date = DateTime::from_timestamp(BUILD_TIMESTAMP as i64, 0)
            .unwrap_or_else(|| Utc::now());
        let expected_signature = Self::generate_security_signature(&self.customer_id, &build_date);
        
        self.security_signature == expected_signature
    }
}

// Secure license manager with enhanced validation
pub struct LicenseManager {
    licenses: HashMap<String, License>,
    config_path: String,
    security_manager: ConfigManager,
}

impl LicenseManager {
    pub fn new(config_path: String) -> Self {
        Self {
            licenses: HashMap::new(),
            config_path,
            security_manager: ConfigManager::new(),
        }
    }

    pub fn load_license(&mut self, license_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Layer 1: File existence check
        if !std::path::Path::new(license_path).exists() {
            return Err("License file not found".into());
        }

        // Layer 2: Read and parse license
        let license_data = std::fs::read_to_string(license_path)?;
        let license: License = serde_json::from_str(&license_data)?;
        
        // Layer 3: Multi-layer validation
        if self.validate_license(&license) {
            self.licenses.insert(license.customer_id.clone(), license);
            Ok(())
        } else {
            Err("License validation failed".into())
        }
    }

    fn validate_license(&self, license: &License) -> bool {
        // Layer 1: Basic license validation
        let basic_valid = license.is_valid();
        
        // Layer 2: Signature validation
        let signature_valid = license.validate_signature();
        
        // Layer 3: Security manager validation
        let security_valid = self.security_manager.validate_feature(
            &license.customer_id, 
            "license_validation"
        );
        
        // Layer 4: Expiration check
        let expiration_valid = license.days_remaining() > 0;
        
        // All layers must pass
        basic_valid && signature_valid && security_valid && expiration_valid
    }

    pub fn validate_license_access(&self, customer_id: &str, feature: &str) -> bool {
        if let Some(license) = self.licenses.get(customer_id) {
            // Use secure validation
            let license_valid = license.is_valid();
            let feature_available = license.has_feature(feature);
            let security_valid = self.security_manager.validate_feature(customer_id, feature);
            
            license_valid && feature_available && security_valid
        } else {
            false
        }
    }

    pub fn get_license_info(&self, customer_id: &str) -> Option<&License> {
        self.licenses.get(customer_id)
    }

    pub fn generate_license(&self, customer_id: String, features: Vec<String>) -> License {
        // Generate license with hardcoded expiration
        License::new(customer_id, features)
    }

    pub fn save_license(&self, license: &License, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Validate license before saving
        if !self.validate_license(license) {
            return Err("Cannot save invalid license".into());
        }
        
        let license_json = serde_json::to_string_pretty(license)?;
        std::fs::write(output_path, license_json)?;
        Ok(())
    }

    pub fn get_security_report(&self, customer_id: &str) -> Option<HashMap<String, String>> {
        self.security_manager.get_security_report(customer_id)
    }

    pub fn get_hardcoded_expiration_info(&self) -> HashMap<String, String> {
        let mut info = HashMap::new();
        info.insert("build_timestamp".to_string(), BUILD_TIMESTAMP.to_string());
        info.insert("hardcoded_expiration_days".to_string(), HARDCODED_EXPIRATION_DAYS.to_string());
        info.insert("security_level".to_string(), "Maximum".to_string());
        
        // Calculate actual expiration date
        let build_date = DateTime::from_timestamp(BUILD_TIMESTAMP as i64, 0)
            .unwrap_or_else(|| Utc::now());
        let expiration = build_date + chrono::Duration::days(HARDCODED_EXPIRATION_DAYS as i64);
        info.insert("expiration_date".to_string(), expiration.to_rfc3339());
        
        info
    }
}

// Enhanced feature access control
pub struct FeatureAccess {
    manager: LicenseManager,
    access_log: HashMap<String, u32>,
}

impl FeatureAccess {
    pub fn new(config_path: String) -> Self {
        Self {
            manager: LicenseManager::new(config_path),
            access_log: HashMap::new(),
        }
    }

    pub fn check_access(&self, customer_id: &str, feature: &str) -> bool {
        // Log access attempt
        let access_count = self.access_log.get(customer_id).unwrap_or(&0) + 1;
        
        // Check access limits
        if access_count > 1000 {
            return false; // Too many access attempts
        }
        
        // Validate access
        self.manager.validate_license_access(customer_id, feature)
    }

    pub fn get_available_features(&self, customer_id: &str) -> Vec<String> {
        if let Some(license) = self.manager.get_license_info(customer_id) {
            if license.is_valid() {
                license.features.clone()
            } else {
                Vec::new()
            }
        } else {
            Vec::new()
        }
    }

    pub fn get_security_status(&self, customer_id: &str) -> HashMap<String, String> {
        let mut status = HashMap::new();
        
        // License status
        if let Some(license) = self.manager.get_license_info(customer_id) {
            status.insert("license_valid".to_string(), license.is_valid().to_string());
            status.insert("days_remaining".to_string(), license.days_remaining().to_string());
            status.insert("signature_valid".to_string(), license.validate_signature().to_string());
        } else {
            status.insert("license_valid".to_string(), "false".to_string());
        }
        
        // Security report
        if let Some(security_info) = self.manager.get_security_report(customer_id) {
            for (key, value) in security_info {
                status.insert(format!("security_{}", key), value);
            }
        }
        
        // Access logging
        let access_count = self.access_log.get(customer_id).unwrap_or(&0);
        status.insert("access_attempts".to_string(), access_count.to_string());
        
        status
    }
}
