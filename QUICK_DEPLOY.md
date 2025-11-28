# Quick Deployment Guide

## Step-by-Step Deployment

### 📦 Backend Deployment (Railway)

1. **Sign up/Login**: [railway.app](https://railway.app) → Sign in with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `job-scraping` repository

3. **Configure Environment Variables**:
   Go to Settings → Variables → Add:
   
   ```env
   SECRET_KEY=<generate-with-command-below>
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   CORS_ALLOWED_ORIGINS=<add-after-frontend-deploy>
   ```

   **Generate SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. **Deploy**: Railway will auto-deploy. Wait for deployment to complete.

5. **Get Backend URL**:
   - Go to Settings → Networking
   - Generate public domain (e.g., `your-app.up.railway.app`)
   - **Copy this URL** - you'll need it for frontend

---

### 🎨 Frontend Deployment (Vercel)

1. **Sign up/Login**: [vercel.com](https://vercel.com) → Sign in with GitHub

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your `job-scraping` repository

3. **Configure Project**:
   - Framework: **Create React App**
   - Root Directory: **frontend**
   - Build Command: **npm run build** (auto-detected)
   - Output Directory: **build** (auto-detected)

4. **Add Environment Variable**:
   Go to Settings → Environment Variables → Add:
   
   ```env
   REACT_APP_API_URL=https://your-railway-app.up.railway.app
   ```
   
   Replace with your actual Railway backend URL from step above.

5. **Deploy**: Click "Deploy" → Wait 2-3 minutes

6. **Get Frontend URL**: Your app will be live at `your-app.vercel.app`

---

### 🔗 Connect Frontend & Backend

1. **Update Backend CORS**:
   - Go back to Railway → Your Service → Variables
   - Update `CORS_ALLOWED_ORIGINS`:
     ```env
     CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
     ```
   - Redeploy backend

2. **Test Connection**:
   - Open your Vercel frontend URL
   - Try searching for a job
   - Check browser console for any errors

---

## ✅ Checklist

- [ ] Backend deployed on Railway
- [ ] Backend URL copied
- [ ] Frontend deployed on Vercel
- [ ] Frontend URL copied
- [ ] Environment variables set (both services)
- [ ] CORS updated with frontend URL
- [ ] Backend redeployed after CORS update
- [ ] Tested job search functionality

---

## 🐛 Common Issues

**CORS Error**: Update `CORS_ALLOWED_ORIGINS` in Railway with your Vercel URL

**Cannot Connect**: Check `REACT_APP_API_URL` in Vercel matches Railway URL

**Chrome/ChromeDriver Error**: Railway should handle this via `nixpacks.toml`

**Build Fails**: Check logs in Railway/Vercel dashboard for specific errors

---

## 📝 Files Created for Deployment

- `vercel.json` - Vercel configuration
- `Procfile` - Railway process definition
- `railway.json` - Railway configuration
- `nixpacks.toml` - Chrome/Chromium installation for Railway
- `DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- `ENV_EXAMPLE.md` - Environment variables reference

---

## 🚀 After Deployment

Updates are automatic:
- Push to GitHub → Both services auto-deploy
- No manual steps needed for updates

---

Need help? Check `DEPLOYMENT_GUIDE.md` for detailed troubleshooting.

