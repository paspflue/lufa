<div align="center">
  <img src="lufa/static/assets/logo/lufa_logo.svg" alt="LUFA Logo" width="300">
</div>

# LUFA - Logging UI for automations

A lightweight dashboard for visualizing and analyzing for Ansible / AWX data. 
It provides quick insights into jobs, templates, and workflows with helpful filters, summaries, and links back to AWX.

## Features
- Overview and detail views for AWX jobs, templates, and workflows
- Powerful filtering and search for efficient analysis
- Compliance-related job marking for compliance tracking and audits
- Optional "Live" mode to periodically refresh data
- Simple configuration for local or production environments
- Runs as a Flask/WSGI app or in Docker

## Requirements
- Python 3.12 (at least 3.12)
- Node.js and npm (for frontend dependency management)
- virtualenv (recommended)
- Optional: Docker (for containerized deployment)
- An SQLite or PostgreSQL database
- An AWX instance or compatible data source
- [Lufa callback plugin](https://github.com/GISA-OSS/lufa-callback)

## Quick Start
### Virtual environment
1) Clone the repository:
```bash
git clone <REPO-URL>
cd lufa
```

2) Create and activate a virtual environment:
```bash
python -m venv .venv
. .venv/bin/activate
```

3) Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4) Install frontend dependencies:
```bash
npm install
bash scripts/copy-assets.sh
```

5) Configure the app:
- Create a configuration file config.py based on the provided example:
```bash
cp config.py.example config.py
```
- Create an instance directory for secrets:
```bash
mkdir -p instance
```

- Store sensitive values (e.g., SECRET_KEY, API keys, DB passwords) in instance/secrets.py.

6) Run the app (development):
```bash
flask --app wsgi.py run
```
By default, the app will be available at http://127.0.0.1:5000.

### Docker
Build and run the container:

1) Build the image:
```bash
docker build -t lufa:latest .
```
or to use a custom base image:
```bash
docker build --build-arg BASE_IMAGE=<my_registry>/<my_org>/<my_image>:<my_tag> -t lufa:latest .
```

2) Run the container (example):
```bash
docker run --rm -p 8080:8080 \
  -e FLASK_ENV=production \
  -v "$(pwd)/instance:/app/instance" \
  lufa:latest
```

Notes:
- Mount instance/ to provide secrets/config inside the container or use environment variables.
- All configuration variables can be specified as environment variables if `LUFA_` is prefixed.
- For production, orchestrate with systemd, Docker Compose, or Kubernetes and set a non-root user where possible.

## Configuration
The application can be configured via configuration files (config.py and instance/secrets.py)
or environment variables (LUFA_ prefix). Typical settings include:
- Database (type, host, port, name, user, password)
- Logging (log level, file path)
- Authentication (local login or directory service)
- API access keys and external endpoints (e.g., AWX base URL)
- UI customization (texts, labels)
- Compliance-related job tracking (via `lufa_compliance_interval` variable in AWX templates)

All configuration parameters are described in config.py.example.

Recommendations:
- Keep secrets only in instance/ or environment variables.
- Use separate configurations per environment (dev/test/prod).
- Never commit secrets to the repository.

## Frontend Dependencies (Node.js/npm)

This project uses Node.js and npm exclusively for managing frontend dependencies such as Bootstrap, 
DataTables, and related libraries. **No build system, bundling, or transpilation is used.**

### Purpose and Workflow

The workflow is intentionally simple:
1. **Dependency Declaration**: All frontend libraries are declared in `package.json`
2. **Download**: Running `npm install` downloads the libraries to `node_modules/`
3. **Copy to Distribution**: The script `scripts/copy-assets.sh` copies the minified production files 
from `node_modules/` to `lufa/static/dist/`
4. **Flask Integration**: Flask serves these static files directly from the `dist/` directory

### Benefits

- **Dependency Scanning**: Dependency scanners and security tools can 
automatically analyze `package.json` and identify vulnerabilities, making security management much easier 
than with manually bundled files
- **Version Management**: Clear versioning and update paths for all frontend libraries
- **Reproducibility**: Consistent dependency versions across development, testing, and production environments
- **No Build Complexity**: No webpack, vite, or other build tools required - just simple file copying

### Updating Frontend Dependencies

To update frontend libraries:
```bash
npm update
bash scripts/copy-assets.sh
```

## Compliance Tracking

The compliance-related feature allows you to mark specific jobs and job templates in AWX for compliance tracking and 
audit purposes. This is particularly useful for organizations that need to track critical configurations and 
security-related automation tasks.

### How it works

**Variable Configuration**: Jobs are marked with compliance-related by setting the `lufa_compliance_interval` variable 
to a positive integer in the job template, workflow template, or schedule. If this variable is not set or is set to `0`
the job is considered non-compliance-related.

Example configuration in AWX:
```yaml
extra_vars:
  lufa_compliance_interval: 7
```

**Callback Plugin Integration**: The [callback plugin](https://github.com/GISA-OSS/lufa-callback) automatically detects 
the presence of this variable when a job starts and transmits this information to the dashboard.

**Database Storage**: The dashboard stores this information in a `compliance_interval` column (int, default: 0)
in the job_templates table.

**Frontend Filtering**: The dashboard frontend provides filtering capabilities,
allowing auditors and administrators to quickly identify and review all compliance-related jobs and templates.

### Use Cases

**Auditors**: Track whether all compliance-related jobs have been successfully executed on designated hosts within the given interval in days.

**System Administrators**: Monitor when compliance-related jobs were last successfully executed on a host and identify
any action items.

**Automation Administrators**: Mark jobs and templates appropriately so they are visible in the dashboard for audit and
compliance evaluations.

### Compliance Logic

- A host is considered **compliant** when all compliance-related jobs have been successfully executed within the interval in days.
- After a successful re-run of a previously failed compliance-related job, the host is automatically marked as
compliant again.
- This flexible marking system can be applied to any job or template as needed.

### Benefits

- **Audit Compliance**: Effortlessly recognize and monitor automation tasks that are critical for compliance
- **Compliance Reporting**: Generate reports specifically for compliance-related jobs
- **Risk Management**: Quickly assess the impact and status of compliance-related automation
- **Operational Oversight**: Provide clear visibility into critical infrastructure changes

## Development
- Use virtualenv and pin dependencies.
- Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Linting and Formatting (ruff)
This project uses Ruff for both linting (ruff check) and code formatting (ruff format).
- Lint the code:
```bash
# Show lint issues
ruff check

# Automatically fix what can be fixed
ruff check --fix
```

- Format the code:
```bash
# Format all files in place
ruff format

# Check formatting without changing files
ruff format --check

```

### Testing
The project uses three types of tests, executed with pytest:
- Unit tests (fast, isolated)
- Integration tests (service-level, database-backed)
- End-to-end (E2E) tests (full flow, closest to real usage)

Integration and E2E test suites can run against both PostgreSQL and SQLite.
By default, an empty Postgres database is required. 
The data is provided as environment variables (POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD).
Database selection can be controlled via pytest `postgres` and `sqlite3` markers.

- Run unit tests:
```bash
cd tests/unit; PYTHONPATH=../..: pytest -v
```

- Run integration tests:
```bash
cd tests/integration; PYTHONPATH=../..: pytest -v
```
or to run only against the sqlite backend:
```bash
cd tests/integration; PYTHONPATH=../..: pytest -m sqlite3 -v
```

- Run E2E tests:
```bash
cd tests/e2e; PYTHONPATH=../..: pytest -v
```

## Disclaimer
This project provides a custom web frontend to visualize outputs from Ansible / AWX and is not affiliated with, endorsed by, or supported by Red Hat, Inc.. The names are used strictly for descriptive purposes of compatibility.
- The AWX Project is a trademark of Red Hat, Inc., used with permission in accordance with the [AWX Trademark Guidelines](https://github.com/ansible/awx-logos/blob/master/TRADEMARKS.md). 
- Ansible is a registered trademark of Red Hat, Inc.   

---
Thank you for using and contributing to LUFA! If you have questions or need help, please open an issue or start a discussion.