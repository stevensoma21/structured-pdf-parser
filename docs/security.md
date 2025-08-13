# Security and Configuration Management

## Overview

The ML Core system includes enterprise-grade security and configuration management features to ensure reliable operation and access control.

## Configuration Management

### License Configuration

The system uses JSON-based configuration files to manage feature access and licensing:

```json
{
  "customer_id": "customer_001",
  "features": ["module_extraction", "step_extraction"],
  "expires_at": "2024-01-15T00:00:00Z",
  "metadata": {
    "version": "1.0.0",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Configuration Validation

The system validates configuration files to ensure:
- Required fields are present
- Expiration dates are valid
- Feature lists are properly formatted

## Feature Access Control

### Available Features

- `module_extraction`: Extract logical modules from documents
- `step_extraction`: Extract procedural steps
- `flow_extraction`: Extract decision flows
- `llm_integration`: LLM-based enhancement features

### Access Control

Feature access is controlled through:
- Configuration validation
- Expiration date checking
- Feature list verification

## Security Features

### Configuration Security

- JSON schema validation
- Expiration date enforcement
- Feature access control
- Configuration integrity checks

### Runtime Security

- Session management
- Access validation
- Error handling
- Graceful degradation

## Usage Examples

### Loading Configuration

```python
from core.config_manager import ConfigManager

# Load configuration
manager = ConfigManager("config/license.json")
if manager.load_config():
    print("Configuration loaded successfully")
```

### Checking Feature Access

```python
from core.config_manager import FeatureAccess

# Check feature access
access = FeatureAccess(manager)
if access.check_access("module_extraction"):
    print("Module extraction available")
```

### Getting Available Features

```python
# Get list of available features
features = access.get_available_features()
print(f"Available features: {features}")
```

## Error Handling

The system includes comprehensive error handling:

- Configuration file not found
- Invalid configuration format
- Expired configuration
- Missing required features
- Access denied errors

## Best Practices

### Configuration Management

1. **Secure Storage**: Store configuration files securely
2. **Regular Updates**: Update configurations before expiration
3. **Backup**: Keep backups of configuration files
4. **Validation**: Always validate configurations before use

### Security Considerations

1. **File Permissions**: Set appropriate file permissions
2. **Network Security**: Secure configuration distribution
3. **Access Control**: Limit access to configuration files
4. **Monitoring**: Monitor configuration usage and access

## Troubleshooting

### Common Issues

1. **Configuration Not Found**
   - Check file path
   - Verify file exists
   - Check file permissions

2. **Configuration Expired**
   - Update configuration file
   - Check expiration date
   - Contact support for renewal

3. **Feature Access Denied**
   - Verify feature is in configuration
   - Check configuration validity
   - Ensure configuration is not expired

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For security-related issues or configuration problems:

- Check the troubleshooting section above
- Review configuration file format
- Contact technical support
- Refer to system logs for detailed error information
