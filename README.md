# the_conf

[![Build Status](https://travis-ci.org/jaesivsm/the_conf.svg?branch=master)](https://travis-ci.org/jaesivsm/the_conf) [![Coverage Status](https://coveralls.io/repos/github/jaesivsm/the_conf/badge.svg?branch=master)](https://coveralls.io/github/jaesivsm/the_conf?branch=master)

A Python configuration management library that merges values from multiple sources (files, command line, environment variables) with schema validation and configurable priority ordering.

## Installation

```bash
pip install the_conf
# or
poetry add the_conf
```

## Quick Start

### 1. Define a Meta Configuration (Schema)

Create a YAML file defining your configuration schema (`myapp.meta.yml`):

```yaml
source_order: ['env', 'files', 'cmd']  # Priority order (first wins)
config_files: ['config.yml']

parameters:
  - database_url:
      type: str
      required: true
      help_txt: Database connection string
  - debug:
      type: bool
      default: false
  - max_connections:
      type: int
      default: 10
      among: [5, 10, 20, 50]  # Valid choices
  - nested:
    - timeout:
        type: int
        default: 30
```

### 2. Load Configuration

```python
from the_conf import TheConf

# Load meta configuration and gather values from all sources
conf = TheConf('myapp.meta.yml')

# Access values
print(conf.database_url)
print(conf.debug)
print(conf.nested.timeout)

# Modify values (writes to main config file)
conf.max_connections = 20
conf.write()
```

### 3. Provide Values from Different Sources

**From environment variables:**
```bash
export DATABASE_URL="postgresql://localhost/mydb"
export NESTED_TIMEOUT="60"
```

**From config file** (`config.yml`):
```yaml
database_url: postgresql://localhost/mydb
debug: true
nested:
  timeout: 45
```

**From command line:**
```bash
python myapp.py --database-url postgresql://localhost/mydb --debug --nested-timeout 60
```

## Source Priority System

The `source_order` defines which source takes precedence when the same parameter is provided from multiple sources. **The first source in the list wins** - later sources do not overwrite values from earlier sources.

**Default order:** `["cmd", "files", "env"]` (command line > files > environment)

**Example with `source_order: ["env", "files", "cmd"]`:**
- If `DEBUG` is set in environment variables, the value from config files or command line will be **ignored**
- This is useful when you want environment variables (e.g., in containers) to always take precedence

## Parameter Options

- `type`: `str`, `int`, `bool`, `list`, `dict`
- `default`: Default value (cannot be combined with `required`)
- `required`: Must be provided from at least one source
- `among`: List of valid choices
- `read_only`: Prevents modification after initial load
- `no_cmd`: Exclude this parameter from command line parsing
- `no_env`: Exclude this parameter from environment variable parsing
- `cmd_line_opt`: Override the auto-generated command line flag
- `help_txt`: Help text for documentation and CLI

## List Parameters

### Simple Lists

```yaml
parameters:
  - allowed_ips:
      type: list
      allowed_ips: {type: str}
```

**From environment:**
```bash
export ALLOWED_IPS_0="192.168.1.1"
export ALLOWED_IPS_1="192.168.1.2"
```

**From file:**
```yaml
allowed_ips:
  - 192.168.1.1
  - 192.168.1.2
```

**In Python:**
```python
conf.allowed_ips.append("192.168.1.3")
print(conf.allowed_ips[0])  # 192.168.1.1
```

### Complex Lists (Lists of Dicts)

```yaml
parameters:
  - servers:
      type: list
      servers:
        - host: {type: str}
        - port: {type: int}
```

**From environment:**
```bash
export SERVERS_0_HOST="localhost"
export SERVERS_0_PORT="8080"
export SERVERS_1_HOST="remote.host"
export SERVERS_1_PORT="8081"
```

**From file:**
```yaml
servers:
  - host: localhost
    port: 8080
  - host: remote.host
    port: 8081
```

**In Python:**
```python
print(conf.servers[0].host)  # localhost
print(conf.servers[0].port)  # 8080
```

**Note:** List parameters are not available via command line arguments due to technical limitations.

## File Encryption

`the_conf` supports encrypted configuration files using AES encryption:

```python
# Save encrypted config
conf = TheConf('myapp.meta.yml')
conf.database_password = "secret"
conf.write('config.yml', passkey='my-encryption-key')

# Load encrypted config
conf = TheConf('myapp.meta.yml', passkey='my-encryption-key')
```

Or via command line/environment:
```bash
python myapp.py --passkey my-encryption-key
# or
export THECONF_PASSKEY="my-encryption-key"
```

## Nested Configuration

Create hierarchical configuration structures:

```yaml
parameters:
  - database:
    - host: {type: str, default: localhost}
    - port: {type: int, default: 5432}
    - credentials:
      - username: {type: str}
      - password: {type: str}
```

Access with dot notation:
```python
conf.database.host
conf.database.credentials.username
```

## Interactive Configuration Generation

Use the interactive mode to generate configuration files:

```python
conf = TheConf('myapp.meta.yml', prompt_values=True)
# Prompts user for required values and generates config file
```

## Design Philosophy

From [this article](http://sametmax.com/les-plus-grosses-roues-du-monde/), a good configuration library should:

- Provide a standardized API to define parameters via a data schema
- Generate command line and environment variable parsers from the schema
- Generate validators from the schema
- Separate program configuration from user parameters
- Support read-only settings and permissions
- Load settings from compatible sources (database, files, APIs, services)
- Support configuration hierarchies with cascading value retrieval
- Be simple enough for small scripts yet powerful for complex applications
- Auto-document settings

## Terminology

- **Meta Configuration**: The schema file (YAML/JSON) that defines parameter names, types, defaults, and validators
- **User Configuration**: The actual values loaded from files, command line, or environment variables

## Development

```bash
# Run tests
make test

# Run linters
make lint

# Build package
make build
```

## License

GPLv3 - See LICENSE file for details
