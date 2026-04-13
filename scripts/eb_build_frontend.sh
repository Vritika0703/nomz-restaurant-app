#!/usr/bin/env bash
# Elastic Beanstalk: produce a fresh frontend/dist on every deploy.
#
# Common reasons React never loads on AWS:
# - Skipping npm run build when dist/ already exists → stale index.html vs missing hashed /assets/*.
# - NODE_ENV=production during npm ci → devDependencies (Vite) not installed → build fails or no output.
# - leader_only build on multi-instance → only one EC2 has dist (see .ebextensions/django.config).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND="${ROOT}/frontend"

if [[ ! -d "${FRONTEND}" ]]; then
  echo "eb_build_frontend: no frontend/ directory."
  exit 1
fi

if [[ -f "${FRONTEND}/package.json" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    if command -v dnf >/dev/null 2>&1; then
      dnf install -y nodejs npm
    elif command -v yum >/dev/null 2>&1; then
      yum install -y nodejs npm
    fi
  fi
  if ! command -v npm >/dev/null 2>&1; then
    echo "eb_build_frontend: npm not available."
    exit 1
  fi

  # EB often sets NODE_ENV=production; that makes npm skip devDependencies, so Vite is missing.
  unset NODE_ENV || true
  export NPM_CONFIG_PRODUCTION=false

  echo "eb_build_frontend: clean dist + npm ci + vite build..."
  rm -rf "${FRONTEND}/dist"
  (
    cd "${FRONTEND}"
    if [[ -f package-lock.json ]] || [[ -f npm-shrinkwrap.json ]]; then
      npm ci
    else
      npm install
    fi
    npm run build
  )
elif [[ -f "${FRONTEND}/dist/index.html" ]]; then
  echo "eb_build_frontend: no package.json; using committed frontend/dist only."
  exit 0
else
  echo "eb_build_frontend: need frontend/package.json or committed frontend/dist."
  exit 1
fi

if [[ ! -f "${FRONTEND}/dist/index.html" ]]; then
  echo "eb_build_frontend: frontend/dist/index.html still missing after build."
  exit 1
fi

assets_dir="${FRONTEND}/dist/assets"
if [[ ! -d "${assets_dir}" ]]; then
  echo "eb_build_frontend: dist/assets directory missing."
  exit 1
fi
if ! compgen -G "${assets_dir}/*" >/dev/null 2>&1; then
  echo "eb_build_frontend: dist/assets is empty — Vite build did not emit JS/CSS."
  exit 1
fi
