# Contributing to Orbital Traffic Impact Analyzer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, Node version, etc.)
- **Error messages and logs**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Possible implementation** approach
- **Examples** from other projects if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure tests pass** (`pytest` for backend, `npm test` for frontend)
6. **Commit with clear messages** following conventional commits
7. **Open a Pull Request** with a clear title and description

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -e .
```

Run tests:
```bash
pytest tests/ -v
```

Run linter:
```bash
flake8 app/
black app/
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Run tests:
```bash
npm test
```

Run linter:
```bash
npm run lint
```

## Code Style Guidelines

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all public functions (Google style)
- Maximum line length: **100 characters**
- Use **Black** for code formatting
- Use **isort** for import sorting

Example:
```python
def calculate_position(satellite_id: int, time: datetime) -> Optional[Dict]:
    """
    Calculate satellite position at specific time.
    
    Args:
        satellite_id: Database ID of satellite
        time: Time to calculate position
        
    Returns:
        Dictionary with position data or None on error
    """
    pass
```

### TypeScript/React (Frontend)

- Follow **Airbnb JavaScript Style Guide**
- Use **TypeScript strict mode**
- Use **functional components** with hooks
- Use **named exports** for components
- Maximum line length: **100 characters**
- Use **Prettier** for code formatting

Example:
```typescript
interface Props {
  satelliteId: number;
  onSelect: (id: number) => void;
}

function SatelliteCard({ satelliteId, onSelect }: Props) {
  // Component implementation
}

export default SatelliteCard;
```

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat(api): add endpoint for historical snapshots

fix(frontend): resolve Cesium initialization race condition

docs(readme): update installation instructions
```

## Testing Guidelines

### Backend Tests

- Write **unit tests** for all services and utilities
- Write **integration tests** for API endpoints
- Use **pytest fixtures** for database setup
- Mock external API calls (CelesTrak, etc.)
- Aim for **>80% code coverage**

Example:
```python
def test_satellite_position_calculation(test_db):
    """Test satellite position calculation."""
    tracker = SatelliteTracker(test_db)
    position = tracker.propagate_position(1)
    
    assert position is not None
    assert -90 <= position['lat'] <= 90
    assert -180 <= position['lon'] <= 180
```

### Frontend Tests

- Write **component tests** using React Testing Library
- Write **integration tests** for user flows
- Test **error handling** and edge cases
- Mock API calls using MSW

Example:
```typescript
test('renders satellite list', () => {
  render(<Sidebar positions={mockPositions} />);
  expect(screen.getByText('STARLINK-1007')).toBeInTheDocument();
});
```

## Documentation

- Update **README.md** for user-facing changes
- Update **API documentation** for endpoint changes
- Add **code comments** for complex logic
- Update **type definitions** when modifying data structures

## Review Process

1. **Automated checks** must pass (linting, tests)
2. **At least one maintainer** must approve
3. **No unresolved conversations**
4. **Branch must be up to date** with main

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

## Questions?

Feel free to open an issue or discussion if you have questions!

Thank you for contributing! 🚀

