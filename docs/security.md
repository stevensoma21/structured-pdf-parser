# Security and Configuration Management

## Overview

The ML Core system includes enterprise-grade security and configuration management features.

## Configuration Management

### License Configuration

```json
{
  "customer_id": "customer_001",
  "features": ["module_extraction", "step_extraction"],
  "expires_at": "2024-01-15T00:00:00Z"
}
```

### Feature Access Control

- module_extraction: Extract logical modules
- step_extraction: Extract procedural steps
- flow_extraction: Extract decision flows
- llm_integration: LLM-based enhancement features

## Usage Examples

```python
from core.config_manager import ConfigManager

manager = ConfigManager("config/license.json")
if manager.load_config():
    print("Configuration loaded successfully")
```
