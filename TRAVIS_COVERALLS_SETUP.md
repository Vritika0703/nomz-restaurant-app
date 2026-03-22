# Travis CI & Coveralls Setup Guide - Team3 Nomz Project

This guide walks you through setting up **Travis CI** for continuous integration and **Coveralls** for code coverage tracking in the Nomz project.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Your Repository](#step-1-prepare-your-repository)
3. [Step 2: Connect GitHub to Travis CI](#step-2-connect-github-to-travis-ci)
4. [Step 3: Create `.travis.yml` Configuration](#step-3-create-travisyml-configuration)
5. [Step 4: Set Up Coveralls Integration](#step-4-set-up-coveralls-integration)
6. [Step 5: Update Dependencies](#step-5-update-dependencies)
7. [Step 6: Test the Setup](#step-6-test-the-setup)
8. [Step 7: Add Status Badges to README](#step-7-add-status-badges-to-readme)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

- GitHub repository access (this project)
- GitHub account with admin or push access
- Basic understanding of CI/CD concepts

---

## Step 1: Prepare Your Repository

### 1.1 Create a `.travis.yml` file

Create a new file named `.travis.yml` in the project root with the following configuration:

```yaml
language: python
python:
  - "3.12"

# Services required for testing
services:
  - postgresql

# PostgreSQL configuration
before_script:
  - psql -c "CREATE DATABASE test_nomz_db;" -U postgres
  - psql -c "CREATE USER travis WITH PASSWORD 'travis';" -U postgres || true
  - psql -c "GRANT ALL PRIVILEGES ON DATABASE test_nomz_db TO travis;" -U postgres

# Install dependencies
install:
  - pip install --upgrade pip
  - pip install -r requirements.txt
  - pip install coverage pytest pytest-django pytest-cov
  - pip install coveralls

# Environment variables for testing
env:
  global:
    - DEBUG=True
    - SECRET_KEY=test-secret-key-for-travis-ci
    - ALLOWED_HOSTS=localhost,127.0.0.1,testserver
    - DB_ENGINE=django.db.backends.postgresql
    - DB_NAME=test_nomz_db
    - DB_USER=postgres
    - DB_PASSWORD=postgres
    - DB_HOST=127.0.0.1
    - DB_PORT=5432
    - USE_S3=False
    - ENVIRONMENT=testing

# Test script
script:
  - python manage.py migrate --no-input
  - python manage.py test --no-input --verbosity=2
  - coverage run --source='.' manage.py test nomz --no-input
  - flake8 nomz --max-line-length=120 --extend-ignore=E203,W503
  - python manage.py check

# Send coverage to Coveralls
after_success:
  - coveralls

# Branches to build
branches:
  only:
    - develop
    - production
    - main

# Notifications (optional)
notifications:
  email:
    - your-email@example.com
  on_success: change
  on_failure: always

# Build timeouts
timeout: 600
```

### 1.2 Create a `.coveragerc` file

Create `.coveragerc` in the project root for coverage configuration:

```ini
[run]
source = .
omit =
    */tests.py
    */test_*.py
    manage.py
    setup.py
    */settings.py
    */migrations/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @abc.abstractmethod
    if 0:
    if False:
    if settings.DEBUG
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

---

## Step 2: Connect GitHub to Travis CI

### 2.1 Access Travis CI

1. Go to **[https://travis-ci.com](https://travis-ci.com)** (note: use .com, not .org)
2. Click **"Sign in with GitHub"**
3. Authorize Travis CI to access your GitHub repositories

### 2.2 Enable the Repository

1. After logging in, you'll see your GitHub repositories
2. Find **team3-mon-spring26** repository
3. Toggle the switch to **ON** (enable the repository)
4. Click on the repository name to view settings

### 2.3 Configure Travis CI Settings (Optional)

In the repository settings on Travis CI:

1. **General**: Keep default settings
2. **Environment Variables**: Add any sensitive keys (if not using GitHub Secrets)
3. **Cron Jobs**: Optionally enable periodic testing
4. **Auto Cancellation**: Enable to cancel old builds when new ones are pushed

---

## Step 3: Create `.travis.yml` Configuration

Already covered in Step 1.1. Ensure the file is in your project root and committed to GitHub.

### 3.1 Verify `.travis.yml` Syntax

Run this locally to check for YAML errors:

```bash
pip install -q travis-lint
travis-lint .travis.yml
```

Or validate online at: **[https://www.yamllint.com](https://www.yamllint.com)**

---

## Step 4: Set Up Coveralls Integration

### 4.1 Connect GitHub to Coveralls

1. Go to **[https://coveralls.io](https://coveralls.io)**
2. Click **"Sign in with GitHub"**
3. Authorize Coveralls to access your GitHub repositories
4. Click **"Add Repository"** or search for your repository
5. Find **team3-mon-spring26** and click the toggle to enable it

### 4.2 Verify Coveralls Configuration

1. Go to the repository page on Coveralls
2. Click **"Settings"** (gear icon)
3. You should see your repository's **Repo Token** (keep this private)
4. The Travis CI integration should be auto-configured once `.travis.yml` has `coveralls` in `after_success`

---

## Step 5: Update Dependencies

### 5.1 Add Testing Dependencies to `requirements.txt`

Add these packages (if not already present):

```text
# Testing and coverage
pytest>=7.4.0
pytest-django>=4.5.2
pytest-cov>=4.1.0
coverage>=7.2.0
coveralls>=3.1.1
flake8>=6.0.0
```

Or install them manually for local testing:

```bash
pip install pytest pytest-django pytest-cov coverage coveralls flake8
```

### 5.2 Create `requirements-dev.txt` (Optional)

For local development, create a separate file for development dependencies:

```text
-r requirements.txt
pytest>=7.4.0
pytest-django>=4.5.2
pytest-cov>=4.1.0
coverage>=7.2.0
coveralls>=3.1.1
flake8>=6.0.0
black>=23.0.0
isort>=5.12.0
```

Install with:

```bash
pip install -r requirements-dev.txt
```

---

## Step 6: Test the Setup

### 6.1 Validate `.travis.yml` Locally

```bash
# Install travis CLI (requires Ruby)
gem install travis

# Validate syntax
travis lint .travis.yml

# Or use yamllint if Python is preferred
pip install yamllint
yamllint .travis.yml
```

### 6.2 Test Coverage Command Locally

```bash
# Activate your virtual environment
source .venv/bin/activate

# Run tests with coverage
coverage run --source='.' manage.py test nomz --no-input

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html to view
```

### 6.3 Commit and Push to Trigger Build

```bash
# Add all files
git add .travis.yml .coveragerc requirements.txt

# Commit
git commit -m "Set up Travis CI and Coveralls integration"

# Push to develop or production
git push origin develop
```

### 6.4 Monitor Travis CI Build

1. Go to **[https://travis-ci.com/github/your-username/team3-mon-spring26](https://travis-ci.com)**
2. Find your repository
3. Watch the build progress in real-time
4. Check logs if build fails

### 6.5 Check Coveralls Report

1. If build succeeds, go to **[https://coveralls.io/github/your-username/team3-mon-spring26](https://coveralls.io)**
2. View your code coverage report
3. Track coverage changes over time

---

## Step 7: Add Status Badges to README

### 7.1 Get Badge URLs

**Travis CI Badge:**
```markdown
[![Build Status](https://travis-ci.com/your-username/team3-mon-spring26.svg?branch=develop)](https://travis-ci.com/github/your-username/team3-mon-spring26)
```

**Coveralls Badge:**
```markdown
[![Coverage Status](https://coveralls.io/repos/github/your-username/team3-mon-spring26/badge.svg?branch=develop)](https://coveralls.io/github/your-username/team3-mon-spring26?branch=develop)
```

### 7.2 Add to README.md

Edit your `README.md` and add badges in the introduction section:

```markdown
# Nomz - Restaurant Search & Review Platform

[![Build Status](https://travis-ci.com/your-username/team3-mon-spring26.svg?branch=develop)](https://travis-ci.com/github/your-username/team3-mon-spring26)
[![Coverage Status](https://coveralls.io/repos/github/your-username/team3-mon-spring26/badge.svg?branch=develop)](https://coveralls.io/github/your-username/team3-mon-spring26?branch=develop)

## Overview
...rest of README
```

---

## Monitoring & Troubleshooting

### Common Issues

#### Issue 1: Build Fails - Database Connection Error

**Symptoms:** Tests fail with PostgreSQL connection errors

**Solution:**
- Verify `before_script` creates the database correctly
- Check environment variables in `.travis.yml`
- Ensure `DB_USER` is `postgres` (default Travis CI user)

#### Issue 2: Coverage Not Appearing on Coveralls

**Symptoms:** Build passes but Coveralls shows no data

**Solution:**
1. Verify `coverage run` command runs successfully locally
2. Check `.coveragerc` file exists and is correct
3. Ensure `coveralls` is in `after_success` step
4. Verify repository is enabled on Coveralls.io
5. Check Coveralls has permission to access your repo

#### Issue 3: Build Timeout

**Symptoms:** Travis CI kills the build after 10 minutes

**Solution:**
- Optimize tests to run faster
- Move time-consuming operations to separate builds
- Increase timeout in `.travis.yml` if necessary (max 50 minutes)

#### Issue 4: Django Migrations Fail

**Symptoms:** Migration error during `python manage.py migrate`

**Solution:**
- Run migrations locally and verify they work
- Check for migration conflicts in your `migrations/` directory
- Ensure `ENVIRONMENT=testing` to use correct database settings

### Monitoring Best Practices

1. **Check Travis CI Dashboard regularly**: [https://travis-ci.com/dashboard](https://travis-ci.com/dashboard)
2. **Review Coverage Changes**: Use Coveralls to track coverage trends
3. **Enable Email Notifications**: Get alerts on build failures
4. **Archive Test Logs**: Save Travis CI build logs for debugging

### Useful Commands

```bash
# View local coverage
coverage report

# Generate HTML coverage
coverage html && open htmlcov/index.html

# Run specific tests
python manage.py test nomz.tests.models --no-input

# Check code style
flake8 nomz --max-line-length=120

# Django system checks
python manage.py check
```

---

## Integration with GitHub

### Branch Protection Rules

To enforce CI checks before merging:

1. Go to GitHub repository settings
2. Navigate to **Branches** → **Branch protection rules**
3. Create a rule for `develop`:
   - Check "Require status checks to pass before merging"
   - Select "Travis CI - Build"
   - Check "Require branches to be up to date before merging"

4. Repeat for `production` branch (optional)

---

## Next Steps

1. ✅ Create `.travis.yml` and `.coveragerc` files
2. ✅ Connect Travis CI to GitHub repository
3. ✅ Connect Coveralls to GitHub repository
4. ✅ Update dependencies (pytest, coverage, coveralls)
5. ✅ Commit and push to trigger first build
6. ✅ Monitor build and coverage reports
7. ✅ Add badges to README
8. ✅ Set up branch protection rules (optional)

---

## References

- [Travis CI Documentation](https://docs.travis-ci.com/)
- [Coveralls Documentation](https://coveralls.io/docs)
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

## Support

For issues or questions:
1. Check Travis CI build logs
2. Review Coveralls repository settings
3. Consult the troubleshooting section above
4. Check GitHub repo actions and warnings

