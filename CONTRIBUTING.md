# Contributing to Monoliet MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Monoliet MCP Server project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/monoliet-mcp-server.git
   cd monoliet-mcp-server
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/monoliet/monoliet-mcp-server.git
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional)
- n8n instance for testing

### Setup Steps

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock black ruff mypy

# 3. Install package in editable mode
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env with your test n8n instance

# 5. Run health check
python health_check.py

# 6. Run tests to verify setup
pytest
```

## Making Changes

### Types of Contributions

We welcome:

- **Bug fixes**: Fix issues in existing code
- **New features**: Add new MCP tools or functionality
- **Documentation**: Improve README, guides, or code comments
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Refactoring**: Improve code quality

### Before You Start

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: Describe what you plan to work on
3. **Get feedback**: Wait for maintainer feedback before major changes
4. **Stay focused**: Keep pull requests small and focused

### Development Workflow

```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# ... edit files ...

# 4. Test your changes
pytest

# 5. Format code
black src/ tests/
ruff check src/ tests/ --fix

# 6. Type check
mypy src/

# 7. Commit changes
git add .
git commit -m "feat: add new feature"

# 8. Push to your fork
git push origin feature/your-feature

# 9. Create pull request on GitHub
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_n8n_client.py

# Run specific test
pytest tests/test_n8n_client.py::TestN8NClient::test_list_workflows

# Run with verbose output
pytest -v
```

### Writing Tests

1. **Location**: Place tests in `tests/` directory
2. **Naming**: Use `test_*.py` for files, `test_*` for functions
3. **Coverage**: Aim for >80% code coverage
4. **Mocking**: Mock external dependencies (n8n API)

Example test:

```python
import pytest
from unittest.mock import AsyncMock
from src.tools.workflows import ListWorkflowsTool

@pytest.mark.asyncio
async def test_list_workflows(mock_n8n_client):
    """Test listing workflows."""
    mock_n8n_client.list_workflows = AsyncMock(
        return_value=[{"id": "1", "name": "Test"}]
    )

    tool = ListWorkflowsTool(mock_n8n_client)
    result = await tool.run({"status": "all"})

    assert result["success"] is True
    assert result["data"]["total_count"] == 1
```

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Tests should be isolated and repeatable
- Use fixtures for common setup

## Code Style

We follow Python best practices and PEP 8.

### Formatting

```bash
# Format code with black
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

```bash
# Lint with ruff
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix
```

### Type Hints

- Use type hints for all function arguments and return values
- Import types from `typing` module
- Use `Optional[T]` for nullable values

Example:

```python
from typing import Dict, List, Optional

async def get_workflows(
    active: Optional[bool] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get workflows with optional filtering.

    Args:
        active: Filter by active status
        limit: Maximum results

    Returns:
        List of workflow objects
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(arg1: str, arg2: int) -> bool:
    """Short description of function.

    Longer description if needed. Explain what the function
    does, any important behavior, or edge cases.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg2 is negative
    """
    pass
```

## Commit Messages

Follow conventional commits format:

```
type(scope): short description

Longer description if needed.

Fixes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### Examples

```bash
feat(tools): add workflow clone tool
fix(client): handle timeout errors correctly
docs(readme): update installation instructions
test(workflows): add tests for search tool
refactor(config): simplify environment loading
```

## Pull Request Process

### Before Submitting

1. ✅ Tests pass: `pytest`
2. ✅ Code formatted: `black src/ tests/`
3. ✅ Linting passes: `ruff check src/ tests/`
4. ✅ Type checking passes: `mypy src/`
5. ✅ Documentation updated
6. ✅ CHANGELOG updated (if applicable)

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How did you test this?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted
- [ ] All tests pass

## Related Issues
Fixes #123
```

### Review Process

1. Automated checks will run (GitHub Actions)
2. Maintainer will review within 1-3 days
3. Address feedback if requested
4. Once approved, PR will be merged

### After Merge

1. Delete your feature branch
2. Pull latest main:
   ```bash
   git checkout main
   git pull upstream main
   ```

## Development Tips

### Debugging

```python
# Use logging instead of print
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
```

### Testing n8n Integration

```bash
# Use health check to verify setup
python health_check.py

# Test specific tool manually
python -c "
import asyncio
from src.config import get_config
from src.n8n_client import N8NClient
from src.tools.workflows import ListWorkflowsTool

async def test():
    config = get_config()
    client = N8NClient(config)
    tool = ListWorkflowsTool(client)
    result = await tool.run({'status': 'all'})
    print(result)
    await client.close()

asyncio.run(test())
"
```

### Common Issues

**Import errors:**
```bash
# Reinstall in editable mode
pip install -e .
```

**Test failures:**
```bash
# Run with verbose output
pytest -vv

# Run single test for debugging
pytest tests/test_file.py::test_function -vv
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Email: support@monoliet.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Monoliet MCP Server! 🎉
