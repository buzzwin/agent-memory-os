# PyPI Distribution Guide for Agent Memory OS

This guide provides step-by-step instructions for distributing Agent Memory OS on PyPI.

## 📋 Prerequisites

### 1. PyPI Account Setup

1. **Create PyPI Account**

   - Go to [PyPI](https://pypi.org/account/register/)
   - Create an account with a unique username
   - Verify your email address

2. **Create TestPyPI Account**

   - Go to [TestPyPI](https://test.pypi.org/account/register/)
   - Create an account (can use same username as PyPI)
   - Verify your email address

3. **Generate API Tokens**
   - **PyPI Token**: Go to [PyPI Account Settings](https://pypi.org/manage/account/) → API tokens → Add API token
   - **TestPyPI Token**: Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/) → API tokens → Add API token
   - Save both tokens securely

### 2. Development Environment

```bash
# Install build tools
pip install build twine wheel

# Install development dependencies
pip install -e .[dev]
```

## 🧪 Pre-Distribution Testing

### 1. Run Comprehensive Test Suite

```bash
# Run all tests
python run_tests.py

# Or run individual test suites
python -m pytest tests/test_regression.py -v
python -m pytest tests/test_integrations.py -v
python -m pytest tests/test_memory.py -v
```

### 2. Build and Test Package

```bash
# Build the package
python build_package.py

# This will:
# - Run all tests
# - Build source distribution and wheel
# - Test installation in virtual environment
# - Validate metadata
```

### 3. Manual Testing

```bash
# Test installation from local build
pip install dist/*.whl

# Test import
python -c "import agent_memory_sdk; print('✅ Import successful')"

# Test basic functionality
python -c "
from agent_memory_sdk import MemoryManager, MemoryType
mm = MemoryManager()
memory = mm.add_memory('Test memory', MemoryType.SEMANTIC, 'test_agent')
print(f'✅ Memory created: {memory.id}')
"
```

## 🚀 Distribution Process

### 1. TestPyPI Upload (Recommended First Step)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ agent-memory-os

# Test functionality
python -c "import agent_memory_sdk; print('✅ TestPyPI installation successful')"
```

### 2. PyPI Upload

```bash
# Upload to PyPI
python -m twine upload dist/*

# Verify upload
pip install agent-memory-os

# Test functionality
python -c "import agent_memory_sdk; print('✅ PyPI installation successful')"
```

## 🔧 Automated Distribution with GitHub Actions

### 1. Set Up GitHub Secrets

In your GitHub repository settings, add these secrets:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TESTPYPI_API_TOKEN`: Your TestPyPI API token

### 2. Trigger Distribution

**For TestPyPI (on every push to main):**

- Push to the `main` branch
- GitHub Actions will automatically:
  - Run all tests
  - Build the package
  - Upload to TestPyPI

**For PyPI (on release):**

- Create a new release on GitHub
- GitHub Actions will automatically:
  - Run all tests
  - Build the package
  - Upload to PyPI

## 📦 Package Configuration

### 1. Version Management

Update version in `setup.py`:

```python
version="0.1.0",  # Increment for each release
```

### 2. Dependencies

Core dependencies are in `requirements.txt`. Optional dependencies are defined in `setup.py`:

```python
extras_require = {
    'langchain': ['langchain>=0.1.0', ...],
    'langgraph': ['langgraph>=0.0.20'],
    'pinecone': ['pinecone>=7.0.0'],
    'postgresql': ['psycopg2-binary>=2.9.0'],
    'api': ['fastapi>=0.100.0', ...],
    'all': [...],  # All optional dependencies
    'dev': [...],  # Development dependencies
}
```

### 3. Installation Options

Users can install with different dependency sets:

```bash
# Core package only
pip install agent-memory-os

# With specific integrations
pip install agent-memory-os[langchain]
pip install agent-memory-os[langgraph]
pip install agent-memory-os[pinecone]
pip install agent-memory-os[postgresql]
pip install agent-memory-os[api]

# With all optional dependencies
pip install agent-memory-os[all]

# Development installation
pip install agent-memory-os[dev]
```

## 🔍 Quality Assurance Checklist

Before each release, ensure:

### ✅ Code Quality

- [ ] All tests pass (`python run_tests.py`)
- [ ] Code is linted (`black .`, `flake8 .`)
- [ ] Type checking passes (`mypy agent_memory_sdk/`)
- [ ] Security scan passes (`bandit -r agent_memory_sdk/`)

### ✅ Documentation

- [ ] README.md is up to date
- [ ] All docstrings are complete
- [ ] Examples work correctly
- [ ] Installation instructions are clear

### ✅ Package Structure

- [ ] `setup.py` is properly configured
- [ ] All required files are included
- [ ] Package metadata is accurate
- [ ] Dependencies are correctly specified

### ✅ Testing

- [ ] Unit tests pass
- [ ] Regression tests pass
- [ ] Integration tests pass
- [ ] Demo scripts work
- [ ] Package installs correctly

### ✅ Distribution

- [ ] Package builds without errors
- [ ] Wheel and source distribution are created
- [ ] Package installs in clean environment
- [ ] All imports work correctly

## 🚨 Common Issues and Solutions

### 1. Build Failures

**Issue**: `setup.py` errors
**Solution**: Check syntax and ensure all imports work

**Issue**: Missing dependencies
**Solution**: Update `requirements.txt` and `setup.py`

### 2. Upload Failures

**Issue**: Authentication errors
**Solution**: Verify API tokens are correct

**Issue**: Package already exists
**Solution**: Increment version number

### 3. Installation Failures

**Issue**: Missing optional dependencies
**Solution**: Install with appropriate extras: `pip install agent-memory-os[all]`

**Issue**: Import errors
**Solution**: Check that all modules are properly included in the package

### 4. Test Failures

**Issue**: Integration tests failing
**Solution**: Ensure optional dependencies are installed for testing

**Issue**: Demo script failures
**Solution**: Check that demo scripts can find the project root

## 📈 Release Process

### 1. Pre-Release Checklist

```bash
# 1. Update version
# Edit setup.py and increment version

# 2. Update changelog
# Add release notes to README.md or CHANGELOG.md

# 3. Run full test suite
python run_tests.py

# 4. Build and test package
python build_package.py

# 5. Test on TestPyPI
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ agent-memory-os
```

### 2. Release Steps

```bash
# 1. Create and push release tag
git tag v0.1.0
git push origin v0.1.0

# 2. Create GitHub release
# Go to GitHub → Releases → Create new release
# Use the tag and add release notes

# 3. Upload to PyPI
python -m twine upload dist/*

# 4. Verify release
pip install agent-memory-os
python -c "import agent_memory_sdk; print('Release successful!')"
```

### 3. Post-Release

- [ ] Update documentation if needed
- [ ] Monitor for issues
- [ ] Respond to user feedback
- [ ] Plan next release

## 🔗 Useful Commands

```bash
# Build package
python setup.py sdist bdist_wheel

# Check package contents
tar -tzf dist/agent-memory-os-*.tar.gz
unzip -l dist/agent_memory_os-*.whl

# Validate package
python -m twine check dist/*

# Test installation
pip install --force-reinstall dist/*.whl

# Clean build artifacts
rm -rf build/ dist/ *.egg-info/
```

## 📞 Support

If you encounter issues during distribution:

1. Check the [PyPI documentation](https://packaging.python.org/tutorials/packaging-projects/)
2. Review the [TestPyPI documentation](https://test.pypi.org/help/)
3. Check GitHub Actions logs for automated builds
4. Verify all prerequisites are met

## 🎉 Success Indicators

Your package is successfully distributed when:

- ✅ Package appears on PyPI: https://pypi.org/project/agent-memory-os/
- ✅ Installation works: `pip install agent-memory-os`
- ✅ Import works: `import agent_memory_sdk`
- ✅ Basic functionality works
- ✅ All integrations work (with appropriate extras)
- ✅ Documentation is accessible and accurate

Congratulations! Your Agent Memory OS package is now available to the Python community! 🚀
