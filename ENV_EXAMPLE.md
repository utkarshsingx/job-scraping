# Environment Variables Reference

## Backend (Railway)

Add these environment variables in Railway Dashboard → Your Service → Variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app,*.railway.app

# CORS Settings (add your Vercel frontend URL after deploying)
CORS_ALLOWED_ORIGINS=https://your-frontend-app.vercel.app

# Port (Railway automatically sets this, but you can specify)
PORT=8000
```

### How to generate SECRET_KEY:

Run this command locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Frontend (Vercel)

Add this environment variable in Vercel Dashboard → Your Project → Settings → Environment Variables:

```env
# Backend API URL (add your Railway backend URL after deploying)
REACT_APP_API_URL=https://your-backend-app.up.railway.app
```

## Important Notes

1. **Update CORS_ALLOWED_ORIGINS** after deploying frontend with the actual Vercel URL
2. **Update REACT_APP_API_URL** after deploying backend with the actual Railway URL
3. **Never commit** `.env` files to Git
4. **Restart services** after updating environment variables:
   - Railway: Redeploy the service
   - Vercel: Redeploy the project

