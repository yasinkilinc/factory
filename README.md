# Backend Factory V1 - Deterministic Code Generator

## 🎯 Amaç

Tek kullanıcı için deterministic, güvenilir, spec-driven backend code generator.

**Kritik Prensipler:**
- ✅ Deterministic pipeline (AI inference yok)
- ✅ Fail-fast validator
- ✅ Spec-driven generation
- ✅ Nested JSON spec (max 4 level)
- ✅ Modular monolith backend üretimi

## 📦 Kurulum

```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### 1. Spec Validate Et
```bash
python cli.py validate examples/simple_crud.json
```

### 2. Backend Kodu Üret
```bash
# Spring Boot
python cli.py generate examples/simple_crud.json --output ./output --backend spring-boot

# Python FastAPI
python cli.py generate examples/simple_crud.json --output ./output --backend python
```

### 3. OpenAPI Contract Üret
```bash
python cli.py openapi examples/simple_crud.json --output ./output/openapi.yaml
```

### 4. Decomposition Advisory Raporu
```bash
python cli.py analyze examples/simple_crud.json
```

## 📋 Spec Format

### Minimal Örnek
```json
{
  "specVersion": "1.0.0",
  "project": {
    "name": "my-service",
    "description": "My backend service"
  },
  "modules": [
    {
      "name": "user",
      "entities": [
        {
          "name": "User",
          "fields": [
            {"name": "id", "type": "uuid", "primary": true},
            {"name": "email", "type": "string", "unique": true},
            {"name": "name", "type": "string"}
          ]
        }
      ],
      "endpoints": [
        {
          "path": "/users",
          "method": "POST",
          "handler": "createUser"
        }
      ]
    }
  ]
}
```

## 🏗️ Mimari

```
Spec JSON → Validator → Code Generator → Output
                ↓
         Decomposition Advisor (optional)
```

## 📁 Output

- Validated spec
- Modular monolith backend code
- OpenAPI contract
- Validation report
- Decomposition advisory (optional)

## 🔮 Roadmap

- **V1**: Backend-only, deterministic core ✅
- **V2**: Frontend generation + BE-FE consistency
- **V3**: Microservice decomposition engine
- **V4**: Multi-platform support

## 📄 Lisans

MIT
