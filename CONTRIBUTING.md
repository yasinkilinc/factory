# Contributing to Backend Factory

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Project Structure

```
backend-factory-v1/
├── src/
│   ├── models/          # Pydantic spec models
│   ├── validators/      # Spec validation
│   ├── generators/      # Code generators
│   ├── analyzer/        # Decomposition advisor
│   └── templates/       # Jinja2 templates
├── examples/            # Example specs
├── tests/              # Unit tests
└── cli.py              # CLI entry point
```

## Adding New Features

### Adding a New Backend Type

1. Create template directory: `src/templates/your-backend/`
2. Add Jinja2 templates
3. Update `BackendGenerator` to support new type
4. Add example in `examples/`

### Adding New Field Types

1. Update `FieldType` enum in `src/models/spec_models.py`
2. Update type mapping in `OpenAPIGenerator`
3. Update template filters if needed
4. Add tests

### Adding New Validators

1. Add validation logic in `src/validators/spec_validator.py`
2. Add corresponding tests in `tests/test_validator.py`

## Coding Standards

- Follow PEP 8
- Use type hints
- Write docstrings
- Add unit tests for new features
- Keep functions deterministic (no randomness)

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validator.py

# Run with coverage
pytest --cov=src tests/
```

## Pull Request Process

1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description
5. Ensure CI passes

## Design Principles

- **Deterministic**: No AI inference, no randomness
- **Fail-fast**: Validate early, fail clearly
- **Spec-driven**: Everything from spec
- **Template-based**: Use Jinja2 templates
- **Backward compatible**: Respect spec versioning
