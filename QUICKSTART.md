# 🚀 Quick Start Guide

## Installation

```bash
# Extract the archive
unzip backend-factory-v1.zip
cd backend-factory-v1

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

## Basic Usage

### 1. Validate a Spec

```bash
python cli.py validate examples/simple_crud.json
```

Expected output:
```
✓ Validation PASSED
✓ Spec is valid and ready for code generation
```

### 2. Generate Backend Code

**Generate Spring Boot backend:**
```bash
python cli.py generate examples/simple_crud.json --output ./my-service --backend spring-boot
```

**Generate Python FastAPI backend:**
```bash
python cli.py generate examples/simple_crud.json --output ./my-service --backend python
```

### 3. Generate OpenAPI Contract

```bash
python cli.py openapi examples/simple_crud.json --output ./openapi.yaml
```

### 4. Analyze for Microservices

```bash
python cli.py analyze examples/ecommerce.json
```

## Running Generated Code

### Spring Boot
```bash
cd my-service
mvn spring-boot:run
```

Access at: http://localhost:8080
H2 Console: http://localhost:8080/h2-console

### Python FastAPI
```bash
cd my-service
pip install -r requirements.txt
python src/main.py
```

Access at: http://localhost:8080
API Docs: http://localhost:8080/docs

## Creating Your Own Spec

Create a `my-spec.json` file:

```json
{
  "specVersion": "1.0.0",
  "project": {
    "name": "my-api",
    "description": "My custom API",
    "port": 8080
  },
  "modules": [
    {
      "name": "my_module",
      "entities": [
        {
          "name": "MyEntity",
          "fields": [
            {"name": "id", "type": "uuid", "primary": true},
            {"name": "name", "type": "string", "nullable": false}
          ]
        }
      ],
      "endpoints": [
        {
          "path": "/items",
          "method": "GET",
          "handler": "getItems",
          "response_body": "MyEntity"
        }
      ]
    }
  ]
}
```

Then generate:
```bash
python cli.py validate my-spec.json
python cli.py generate my-spec.json --output ./my-api --backend python
```

## Common Commands

```bash
# Show version
python cli.py version

# Validate with verbose output
python cli.py validate examples/simple_crud.json --verbose

# Generate with force overwrite
python cli.py generate examples/simple_crud.json --output ./out --force

# Generate JSON OpenAPI
python cli.py openapi examples/simple_crud.json --output api.json --format json

# Save analysis report
python cli.py analyze examples/ecommerce.json --output report.json
```

## Spec Field Types

- `uuid` - UUID primary keys
- `string` - Text fields
- `integer` - Integer numbers
- `float` - Decimal numbers
- `boolean` - True/False
- `datetime` - Timestamp
- `date` - Date only
- `text` - Long text
- `json` - JSON data
- `enum` - Enumeration (requires `enum_values`)

## Next Steps

1. Review the examples in `examples/`
2. Read the full README.md
3. Check CONTRIBUTING.md for development
4. Create your own specs
5. Extend with custom templates

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**"Template not found" error:**
Make sure you're running from the project root directory.

**Validation errors:**
Check that your spec follows the format in the examples.

## Support

- Check examples: `examples/`
- Read docs: `README.md`
- Run tests: `pytest tests/`
