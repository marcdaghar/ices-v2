# Contributing to ICES v2

## How to Contribute

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your feature: `git checkout -b feature/your-feature`
4. **Make your changes** with clear commit messages
5. **Run tests**: `pytest tests/ -v`
6. **Push to your fork** and submit a Pull Request

## Code Style

- Python 3.10+
- Black formatting: `black src/ tests/`
- Type hints: `mypy src/ --strict`
- Linting: `ruff src/`

## Testing

```bash
pytest tests/ -v --cov=src/ --cov-report=html
