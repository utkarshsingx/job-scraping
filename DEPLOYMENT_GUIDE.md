# Deployment Guide: Vercel (Frontend) + Railway (Backend)

This guide will walk you through deploying the Job Scraping application:
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway

---

## Prerequisites

1. **GitHub Account**: Your code should be pushed to GitHub
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Railway Account**: Sign up at [railway.app](https://railway.app)
4. **Backend dependencies**: The backend requires Chrome/Chromium for Selenium (Railway will handle this)

---

## Part 1: Deploy Backend to Railway

### Step 1: Prepare Backend for Production

1. **Add Gunicorn to requirements.txt**:
   ```bash
   echo "gunicorn==21.2.0" >> backend/requirements.txt
   ```

2. **Create Procfile** (Railway will use this):
   ```bash
   echo "web: cd backend && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:\$PORT" > Procfile
   ```

3. **Update Django Settings** (we'll modify `backend/backend/settings.py` for production):
   - Add environment variable support
   - Configure CORS for production
   - Set proper ALLOWED_HOSTS
   - Configure static files

### Step 2: Deploy to Railway

1. **Login to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `job-scraping` repository

3. **Configure Build Settings**:
   - Railway should auto-detect Python
   - **Root Directory**: Leave empty (we'll configure in railway.json)
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**:
   Click on your service → Variables tab → Add these:

   ```
   SECRET_KEY=your-secret-key-here-generate-a-random-string
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.up.railway.app,*.railway.app
   CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   PORT=8000
   ```

   **Important**: 
   - Replace `your-vercel-app.vercel.app` with your actual Vercel domain (you'll get this after deploying frontend)
   - Generate a secure SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

5. **Add Chrome/Chromium Dependencies**:
   Railway needs Chrome for Selenium. Add this to your build:
   
   In Railway → Settings → Build → Add build command:
   ```bash
   apt-get update && apt-get install -y chromium-browser chromium-chromedriver
   ```

   Or use a more efficient approach with `nixpacks.toml` (see Railway-specific config below).

6. **Deploy**:
   - Railway will automatically deploy when you push to GitHub
   - Or click "Deploy" to trigger a manual deployment
   - Wait for the build to complete

7. **Get Your Backend URL**:
   - After deployment, go to Settings → Networking
   - Generate a public domain (e.g., `your-app.up.railway.app`)
   - Copy this URL - you'll need it for the frontend

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend

1. **Create vercel.json** in the root directory:
   ```json
   {
     "buildCommand": "cd frontend && npm install && npm run build",
     "outputDirectory": "frontend/build",
     "devCommand": "cd frontend && npm start",
     "installCommand": "cd frontend && npm install",
     "framework": "create-react-app",
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```

2. **Update .gitignore** (if not already):
   Make sure `frontend/.env` is in `.gitignore`

### Step 2: Deploy to Vercel

1. **Login to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your `job-scraping` repository

3. **Configure Project**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

4. **Add Environment Variables**:
   Go to Settings → Environment Variables → Add:

   ```
   REACT_APP_API_URL=https://your-railway-app.up.railway.app
   ```

   **Important**: Replace `your-railway-app.up.railway.app` with your actual Railway backend URL

5. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete (2-3 minutes)
   - Your app will be live at `your-app.vercel.app`

---

## Part 3: Update CORS Settings

After deploying both:

1. **Update Railway Environment Variables**:
   - Go back to Railway → Your Service → Variables
   - Update `CORS_ALLOWED_ORIGINS`:
     ```
     CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app.vercel.app
     ```
   - Add your Vercel deployment URL
   - Redeploy the backend

2. **Update Vercel Environment Variables** (if needed):
   - Verify `REACT_APP_API_URL` points to your Railway backend
   - Redeploy if you made changes

---

## Part 4: Post-Deployment Checklist

- [ ] Backend is accessible at Railway URL
- [ ] Frontend is accessible at Vercel URL
- [ ] Frontend can connect to backend (check browser console for errors)
- [ ] CORS is properly configured
- [ ] Environment variables are set correctly
- [ ] Database migrations ran successfully (check Railway logs)
- [ ] Selenium/Chrome is working (test a job search)

---

## Troubleshooting

### Backend Issues

1. **ChromeDriver not found**:
   - Railway needs Chrome installed
   - Add Chrome to build process (see Railway config below)
   - Check Railway logs for Chrome-related errors

2. **CORS errors**:
   - Verify `CORS_ALLOWED_ORIGINS` includes your Vercel URL
   - Check that `DEBUG=False` and CORS settings are correct
   - Restart Railway service after updating variables

3. **Database errors**:
   - Railway uses PostgreSQL by default
   - Update `settings.py` to use environment variables for database
   - Or use SQLite (simpler, but not recommended for production)

4. **Build fails**:
   - Check Railway logs for specific errors
   - Verify all dependencies in `requirements.txt`
   - Ensure build commands are correct

### Frontend Issues

1. **Cannot connect to backend**:
   - Verify `REACT_APP_API_URL` environment variable is set
   - Check that it points to your Railway backend URL
   - Ensure Railway backend is running and accessible

2. **Build fails**:
   - Check Vercel build logs
   - Verify `package.json` and dependencies
   - Clear build cache in Vercel settings

3. **404 errors on refresh**:
   - The `vercel.json` rewrites should handle this
   - Verify routing is working correctly

---

## Railway-Specific Configuration

### Option 1: Using Nixpacks (Recommended)

Create `nixpacks.toml` in the root:

```toml
[phases.setup]
nixPkgs = ["python39", "chromium", "chromedriver"]

[phases.install]
cmds = [
    "cd backend",
    "pip install -r requirements.txt"
]

[start]
cmd = "cd backend && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT"
```

### Option 2: Using Build Scripts

Add build scripts to handle Chrome installation in Railway build settings.

---

## Environment Variables Summary

### Railway (Backend)

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app,*.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
PORT=8000
DJANGO_SETTINGS_MODULE=backend.settings
```

### Vercel (Frontend)

```env
REACT_APP_API_URL=https://your-backend.up.railway.app
```

---

## Quick Deploy Commands

After initial setup, updates are automatic:

1. **Update Backend**: Push to GitHub → Railway auto-deploys
2. **Update Frontend**: Push to GitHub → Vercel auto-deploys

---

## Next Steps

1. Set up custom domains (optional)
2. Configure monitoring and logging
3. Set up database backups (if using PostgreSQL)
4. Add CI/CD workflows
5. Set up error tracking (Sentry, etc.)

---

## Support

If you encounter issues:
1. Check Railway logs: Railway Dashboard → Your Service → Deployments → View Logs
2. Check Vercel logs: Vercel Dashboard → Your Project → Deployments → View Build Logs
3. Verify environment variables are set correctly
4. Check CORS configuration matches your frontend URL

