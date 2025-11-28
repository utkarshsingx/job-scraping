# Deployment Files Overview

This document explains all the files created for deployment.

## Configuration Files

### `vercel.json`
**Purpose**: Configures Vercel for frontend deployment  
**Location**: Root directory  
**Contents**:
- Build commands for React app
- Output directory configuration
- Rewrite rules for React Router

### `Procfile`
**Purpose**: Defines the process to run on Railway  
**Location**: Root directory  
**Contents**:
- Runs database migrations
- Starts Gunicorn server on Railway's port

### `railway.json`
**Purpose**: Railway-specific configuration  
**Location**: Root directory  
**Contents**:
- Build and deploy commands
- Restart policy

### `nixpacks.toml`
**Purpose**: Installs Chrome/Chromium for Selenium on Railway  
**Location**: Root directory  
**Contents**:
- Python and Chrome dependencies
- Installation commands
- Start command

## Updated Files

### `backend/backend/settings.py`
**Changes**:
- Reads `SECRET_KEY` from environment variable
- Reads `DEBUG` from environment variable
- Reads `ALLOWED_HOSTS` from environment variable (comma-separated)
- Reads `CORS_ALLOWED_ORIGINS` from environment variable (comma-separated)
- Maintains backward compatibility with development defaults

### `backend/requirements.txt`
**Changes**:
- Added `gunicorn==21.2.0` for production WSGI server

## Documentation Files

### `DEPLOYMENT_GUIDE.md`
Comprehensive deployment guide with:
- Detailed step-by-step instructions
- Troubleshooting section
- Configuration options
- Post-deployment checklist

### `QUICK_DEPLOY.md`
Quick reference guide with:
- Simplified step-by-step process
- Essential checklist
- Common issues and fixes

### `ENV_EXAMPLE.md`
Environment variables reference:
- All required environment variables
- Where to set them
- How to generate values

## Next Steps

1. **Review the deployment files** to understand what they do
2. **Follow QUICK_DEPLOY.md** for fastest deployment
3. **Refer to DEPLOYMENT_GUIDE.md** if you encounter issues
4. **Use ENV_EXAMPLE.md** as reference for environment variables

## Important Notes

- All files are committed to Git
- Environment variables are NOT in Git (use platform settings)
- `.env` files should be in `.gitignore`
- Update CORS settings after deploying both services

