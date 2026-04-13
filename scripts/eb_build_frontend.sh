#!/usr/bin/env bash
# Elastic Beanstalk: ensure frontend/dist exists (committed dist and/or npm build).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND="${ROOT}/frontend"

if [[ ! -d "${FRONTEND}" ]]; then
  echo "eb_build_frontend: no frontend/ directory; skipping."
  exit 0
fi

if [[ -f "${FRONTEND}/dist/index.html" ]]; then
  echo "eb_build_frontend: frontend/dist already present."
  exit 0
fi

if [[ -f "${FRONTEND}/package.json" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    if command -v dnf >/dev/null 2>&1; then
      dnf install -y nodejs npm
    elif command -v yum >/dev/null 2>&1; then
      yum install -y nodejs npm
    fi
  fi
  if command -v npm >/dev/null 2>&1; then
    (
      cd "${FRONTEND}"
      if [[ -f package-lock.json ]] || [[ -f npm-shrinkwrap.json ]]; then
        npm ci
      else
        npm install
      fi
      npm run build
    )
  else
    echo "eb_build_frontend: npm not available and dist/ missing."
    exit 1
  fi
else
  echo "eb_build_frontend: no frontend/package.json and no committed frontend/dist."
  exit 1
fi

if [[ ! -f "${FRONTEND}/dist/index.html" ]]; then
  echo "eb_build_frontend: frontend/dist/index.html still missing after build."
  exit 1
fi
