# Contributing

Thank you for your interest in contributing! 🎉

## How to Contribute

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/video-script-writer.git`
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Make changes** and add tests
5. **Run tests**: `pytest tests/ -v`
6. **Commit**: `git commit -m "feat: your feature description"`
7. **Push**: `git push origin feature/your-feature`
8. **Open a Pull Request**

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e .
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=src/
```

## Code Style

- Follow PEP 8
- Add type hints to function signatures
- Write docstrings for public functions
- Keep functions focused and small

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Include expected vs actual behavior
- Include Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the MIT License.