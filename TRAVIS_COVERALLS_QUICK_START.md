# Travis CI & Coveralls Quick Start Checklist

Quick reference for setting up Travis CI and Coveralls integration.

---

## ✅ Phase 1: Local Preparation (Do This First)

- [ ] **Review Configuration Files**
  - [ ] `.travis.yml` exists and is valid YAML
  - [ ] `.coveragerc` exists with coverage settings
  - [ ] Testing dependencies added to `requirements.txt`

- [ ] **Test Coverage Locally**
  ```bash
  source .venv/bin/activate
  coverage run --source='.' manage.py test nomz --no-input
  coverage report
  ```

- [ ] **Verify Django Setup**
  ```bash
  python manage.py check
  python manage.py migrate --plan
  python manage.py test nomz --no-input
  ```

- [ ] **Install Dev Dependencies Locally**
  ```bash
  pip install -r requirements.txt
  pip install pytest pytest-django pytest-cov coverage coveralls flake8
  ```

---

## ✅ Phase 2: GitHub & Version Control

- [ ] **Commit Configuration Files**
  ```bash
  git add .travis.yml .coveragerc requirements.txt
  git commit -m "Set up Travis CI and Coveralls integration"
  git push origin develop
  ```

- [ ] **Verify Commits**
  - [ ] `.travis.yml` in repository root
  - [ ] `.coveragerc` in repository root
  - [ ] Testing dependencies in `requirements.txt`

---

## ✅ Phase 3: Travis CI Setup (Account Creation)

- [ ] **Access Travis CI**
  - [ ] Visit [https://travis-ci.com](https://travis-ci.com)
  - [ ] Click "Sign in with GitHub"
  - [ ] Authorize Travis CI app

- [ ] **Enable Repository**
  - [ ] Log in to Travis CI dashboard
  - [ ] Find `team3-mon-spring26` repository
  - [ ] Toggle **ON** to enable

- [ ] **Configure Settings** (Optional)
  - [ ] General settings review
  - [ ] Enable/disable email notifications
  - [ ] Configure cron jobs if needed

---

## ✅ Phase 4: Coveralls Setup (Account Creation)

- [ ] **Access Coveralls**
  - [ ] Visit [https://coveralls.io](https://coveralls.io)
  - [ ] Click "Sign in with GitHub"
  - [ ] Authorize Coveralls app

- [ ] **Enable Repository**
  - [ ] Log in to Coveralls dashboard
  - [ ] Click "Add Repository"
  - [ ] Find and enable `team3-mon-spring26`
  - [ ] Note: Repository token auto-configured via Travis CI

---

## ✅ Phase 5: First Build Test

- [ ] **Trigger Build**
  - [ ] Push code to `develop` or `production` branch
  - [ ] Or commit to any branch with `[ci skip]` in message to skip (for testing)

- [ ] **Monitor Travis CI**
  - [ ] Go to [https://travis-ci.com/dashboard](https://travis-ci.com/dashboard)
  - [ ] Watch build progress in real-time
  - [ ] Review build logs if any step fails

- [ ] **Check Results**
  - [ ] Wait for tests to complete (5-15 minutes typically)
  - [ ] Verify all steps passed (green ✅)
  - [ ] Check Coveralls for coverage report

- [ ] **Troubleshoot Issues** (if any)
  - [ ] Review Travis CI build logs
  - [ ] Check `.travis.yml` syntax
  - [ ] Verify environment variables
  - [ ] Test locally first

---

## ✅ Phase 6: GitHub Integration

- [ ] **Add Status Badges to README.md**
  - [ ] Travis CI: `[![Build Status](https://travis-ci.com/YOUR-USERNAME/team3-mon-spring26.svg?branch=develop)](https://travis-ci.com/github/YOUR-USERNAME/team3-mon-spring26)`
  - [ ] Coveralls: `[![Coverage Status](https://coveralls.io/repos/github/YOUR-USERNAME/team3-mon-spring26/badge.svg?branch=develop)](https://coveralls.io/github/YOUR-USERNAME/team3-mon-spring26?branch=develop)`

- [ ] **Set Branch Protection** (Optional but Recommended)
  - [ ] Go to repository Settings → Branches
  - [ ] Create protection rule for `develop`:
    - [ ] "Require status checks to pass before merging"
    - [ ] Select "Travis CI - Build"
    - [ ] "Require branches to be up to date before merging"
  - [ ] Repeat for `production` branch

---

## ✅ Phase 7: Ongoing Maintenance

- [ ] **Monitor Builds**
  - [ ] Review build status on every push
  - [ ] Fix failing builds immediately

- [ ] **Track Coverage**
  - [ ] Check Coveralls after each build
  - [ ] Aim to maintain or increase coverage percentage
  - [ ] Review coverage trends over time

- [ ] **Update Dependencies**
  ```bash
  pip list --outdated
  # Update as needed, then re-run tests
  pip install --upgrade <package>
  ```

- [ ] **Review Logs**
  - [ ] Save important build logs
  - [ ] Debug failed builds using Travis CI interface

---

## 🔗 Quick Links

| Service | URL | Purpose |
|---------|-----|---------|
| Travis CI Dashboard | [https://travis-ci.com/dashboard](https://travis-ci.com/dashboard) | View build status |
| Repository Builds | [https://travis-ci.com/github/USERNAME/team3-mon-spring26](https://travis-ci.com/github/USERNAME/team3-mon-spring26) | Specific repo builds |
| Coveralls Dashboard | [https://coveralls.io/dashboard](https://coveralls.io/dashboard) | View coverage reports |
| Repository Coverage | [https://coveralls.io/github/USERNAME/team3-mon-spring26](https://coveralls.io/github/USERNAME/team3-mon-spring26) | Specific repo coverage |
| Travis CI Docs | [https://docs.travis-ci.com](https://docs.travis-ci.com) | Documentation |

---

## 🚨 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Build doesn't start | Check `.travis.yml` committed to repo; wait 1-2 min for Travis to detect |
| Database connection error | Verify `DB_USER=postgres` and database created in `before_script` |
| Coverage not on Coveralls | Run `coverage run` locally to verify; check `.coveragerc` |
| Permission denied error | Ensure user has write access to repository |
| Build timeout | Optimize tests; move long-running tests to separate builds |
| Migrations fail | Run migrations locally first; ensure `ENVIRONMENT=testing` |

---

## 📝 Notes

- Replace `YOUR-USERNAME` in badges with actual GitHub username
- `.travis.yml` builds only on `develop`, `production`, `main` branches
- Coveralls shows coverage trends over time (useful for tracking improvements)
- Email notifications configured for failed builds by default
- Cache is not enabled (can be added later for faster builds)

---

## Next Document to Read

After completing setup, refer to [TRAVIS_COVERALLS_SETUP.md](TRAVIS_COVERALLS_SETUP.md) for detailed information and troubleshooting.
