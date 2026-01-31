# Zion Config

Django-inspired, reusable configuration management for Python applications.

## Overview

Zion Config provides a flexible and extensible configuration system that allows you to:
- Centralize application settings in a single module
- Define reusable configuration classes with prefixed namespaces
- Override default values from a global settings module
- Validate required settings
- Transform configuration values with custom logic

## Installation

For now, there is no future plan to publish the packages in PyPI.
So with the following `uv` command, it can be installed.

```bash
uv add git+https://github.com/gwainor/zion-python#subdirectory=packages/config
```

## Quick Start

### 1. Create a Settings Module

Create a Python module to hold your application settings (e.g., `myapp/settings.py`):

```python
# myapp/settings.py
DEBUG = True
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
```

### 2. Set the Environment Variable

Tell Zion Config where to find your settings module:

```bash
# .env
ZION_SETTINGS_MODULE=myapp.settings
```

### 3. Access Settings

```python
from zion.config import settings

print(settings.DEBUG)  # True
print(settings.DATABASE_HOST)  # "localhost"
```

## AppConf - Reusable Configuration Classes

`AppConf` allows you to create reusable configuration classes with automatic prefixing and intelligent defaults.

### Basic Usage

```python
from zion.config import AppConf, settings

class AuthConf(AppConf):
    # Define configuration with defaults
    SESSION_TIMEOUT = 3600
    USE_JWT = False

    class Meta:
        prefix = "auth"  # Settings will be prefixed with AUTH_

# Access the prefixed settings
print(settings.AUTH_SESSION_TIMEOUT)  # 3600
print(settings.AUTH_USE_JWT)  # False
```

### Overriding Defaults

Values defined in your settings module override the defaults:

```python
# myapp/settings.py
AUTH_SESSION_TIMEOUT = 7200
AUTH_USE_JWT = True
```

```python
from zion.config import AppConf, settings

class AuthConf(AppConf):
    SESSION_TIMEOUT = 3600  # Default value
    USE_JWT = False  # Default value

    class Meta:
        prefix = "auth"

print(settings.AUTH_SESSION_TIMEOUT)  # 7200 (overridden)
print(settings.AUTH_USE_JWT)  # True (overridden)
```

### Custom Configuration Logic

Use `configure_<setting_name>` methods to transform or validate individual settings:

```python
class DatabaseConf(AppConf):
    HOST = "localhost"
    PORT = 5432

    class Meta:
        prefix = "db"

    def configure_port(self, value):
        # Ensure port is an integer
        return int(value)

    def configure_host(self, value):
        # Validate hostname
        if not value:
            raise ValueError("Database host cannot be empty")
        return value.lower()
```

### Global Configuration Method

Override the `configure()` method to add computed settings or perform complex initialization:

```python
class CacheConf(AppConf):
    BACKEND = "redis"
    HOST = "localhost"
    PORT = 6379

    class Meta:
        prefix = "cache"

    def configure(self):
        # Add a computed setting
        backend = self.configured_data["BACKEND"]
        host = self.configured_data["HOST"]
        port = self.configured_data["PORT"]

        self.configured_data["CONNECTION_STRING"] = f"{backend}://{host}:{port}"
        return self.configured_data

print(settings.CACHE_CONNECTION_STRING)  # "redis://localhost:6379"
```

### Required Settings

Specify required settings that must be defined in the settings module:

```python
class EmailConf(AppConf):
    FROM_ADDRESS = None
    SMTP_HOST = None

    class Meta:
        prefix = "email"
        required = ["FROM_ADDRESS", "SMTP_HOST"]  # Will raise ValueError if missing

# This will raise ValueError if EMAIL_FROM_ADDRESS or EMAIL_SMTP_HOST
# are not defined in your settings module
```

### Alternative Settings Holder

By default, `AppConf` reads from the global `settings` object. You can specify a different settings holder:

```python
class CustomConf(AppConf):
    SOME_VALUE = "default"

    class Meta:
        prefix = "custom"
        holder = "myapp.config.custom_settings"  # Path to custom settings object
```

## API Reference

### `settings`

The global settings object that loads configuration from the module specified by the `ZION_SETTINGS_MODULE` environment variable.

**Attributes:**
- All uppercase attributes from your settings module are accessible as attributes

**Methods:**
- `configure(config_module_name: str)`: Reconfigure settings from a different module

### `AppConf`

Base class for reusable configuration.

**Class Attributes:**
- Uppercase attributes become configuration settings (automatically prefixed)

**Inner Meta Class:**
- `prefix` (required): String prefix for all settings (e.g., "auth" → "AUTH_")
- `holder` (optional): Import path to alternative settings holder (defaults to global `settings`)
- `required` (optional): List of setting names that must be defined in the settings module

**Methods:**
- `configure_<setting_name>(self, value)`: Transform or validate a specific setting
- `configure(self)`: Override to add computed settings or perform complex initialization
- `configured_data`: Property that returns all configured settings as a dictionary

### `import_attribute(import_path, exception_handler=None)`

Utility function to import a specific attribute from a module path.

**Parameters:**
- `import_path`: String in format "module.path.AttributeName"
- `exception_handler`: Optional callback for handling import errors

**Returns:**
- The imported attribute

## Environment Variables

- `ZION_SETTINGS_MODULE`: Required. Import path to your settings module (e.g., "myapp.settings")

## Best Practices

1. **Organize by Feature**: Create separate `AppConf` classes for different features (auth, database, cache, etc.)
2. **Use Meaningful Prefixes**: Choose prefixes that clearly indicate the configuration domain
3. **Validate Early**: Use `configure_*` methods to validate settings at startup
4. **Document Defaults**: Clearly document what each setting does and its default value
5. **Mark Required Settings**: Use `Meta.required` to catch missing configuration early

## Examples

### Complete Application Configuration

```python
# config/settings.py
DEBUG = True

# Database settings
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "myapp"

# Auth settings
AUTH_SESSION_TIMEOUT = 7200
AUTH_SECRET_KEY = "secret-key-here"

# Cache settings
CACHE_BACKEND = "redis"
CACHE_HOST = "redis.local"
```

```python
# config/__init__.py
from zion.config import AppConf, settings

class DatabaseConf(AppConf):
    HOST = "localhost"
    PORT = 5432
    NAME = "defaultdb"

    class Meta:
        prefix = "db"

class AuthConf(AppConf):
    SESSION_TIMEOUT = 3600
    SECRET_KEY = None

    class Meta:
        prefix = "auth"
        required = ["SECRET_KEY"]

    def configure_session_timeout(self, value):
        # Ensure timeout is positive
        if value <= 0:
            raise ValueError("Session timeout must be positive")
        return value

class CacheConf(AppConf):
    BACKEND = "memory"
    HOST = "localhost"
    PORT = 6379

    class Meta:
        prefix = "cache"

    def configure(self):
        # Build connection string
        backend = self.configured_data["BACKEND"]
        host = self.configured_data["HOST"]
        port = self.configured_data["PORT"]
        self.configured_data["URL"] = f"{backend}://{host}:{port}"
        return self.configured_data

# Now all settings are available
print(settings.DB_HOST)  # "localhost"
print(settings.AUTH_SESSION_TIMEOUT)  # 7200
print(settings.CACHE_URL)  # "redis://redis.local:6379"
```

## License

See the main project LICENSE file.
