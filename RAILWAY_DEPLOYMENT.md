# 🚀 Railway Deployment Guide

## 📋 Overview

Deploy FastHub to Railway in **10 minutes** with automatic CI/CD from GitHub.

**What you'll get:**
- ✅ Live backend API
- ✅ Live frontend app
- ✅ PostgreSQL database
- ✅ Auto-deploy on `git push`
- ✅ $5 FREE credit (~1 month testing)

---

## 🎯 Prerequisites

1. ✅ GitHub account (already have)
2. ✅ FastHub project on GitHub (already done)
3. ⏳ Railway account (will create)

---

## 📝 Step-by-Step Instructions

### **STEP 1: Create Railway Account**

1. Go to: https://railway.app
2. Click: **"Start a New Project"** or **"Login"**
3. Choose: **"Login with GitHub"** (easiest)
4. Authorize Railway to access GitHub
5. Confirm email (if required)

**You'll get:** $5 FREE credit

---

### **STEP 2: Connect GitHub Repository**

1. Railway Dashboard → **"New Project"**
2. Choose: **"Deploy from GitHub repo"**
3. Railway will ask for access → Click **"Authorize Railway"**
4. Select: **"Only select repositories"**
5. Check: **`Fasthub`**
6. Click: **"Install"**

---

### **STEP 3: Deploy Backend**

#### **3.1. Select Backend Service:**

1. Railway will detect `fasthub-backend/` folder
2. Click on **"fasthub-backend"** service
3. Railway will automatically:
   - ✅ Detect `Dockerfile`
   - ✅ Build Docker image
   - ✅ Start deployment

#### **3.2. Add Environment Variables:**

Click on **"fasthub-backend"** → **"Variables"** tab

**Add these variables:**

```
DATABASE_URL=postgresql://postgres:postgres@postgres.railway.internal:5432/fasthub
SECRET_KEY=<generate-random-32-character-string>
BACKEND_CORS_ORIGINS=https://<your-frontend-domain>.railway.app
ENVIRONMENT=production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**How to generate SECRET_KEY:**
```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32
```

#### **3.3. Generate Backend Domain:**

1. **"fasthub-backend"** service → **"Settings"** → **"Networking"**
2. Click: **"Generate Domain"**
3. Copy URL: `https://fasthub-backend-production.railway.app`
4. **Save this URL** - you'll need it for frontend!

---

### **STEP 4: Deploy PostgreSQL Database**

1. In Railway project → Click **"+ New"**
2. Choose: **"Database"** → **"PostgreSQL"**
3. Railway will automatically:
   - ✅ Create database
   - ✅ Connect to backend
   - ✅ Set `DATABASE_URL` variable

**That's it!** Database is ready.

---

### **STEP 5: Deploy Frontend**

#### **5.1. Select Frontend Service:**

1. Railway will detect `fasthub-frontend/` folder
2. Click on **"fasthub-frontend"** service

#### **5.2. Add Environment Variables:**

Click **"Variables"** tab

**Add:**

```
VITE_API_URL=https://fasthub-backend-production.railway.app/api/v1
```

**Replace** `fasthub-backend-production.railway.app` with **your actual backend URL** from Step 3.3!

#### **5.3. Generate Frontend Domain:**

1. **"fasthub-frontend"** service → **"Settings"** → **"Networking"**
2. Click: **"Generate Domain"**
3. Copy URL: `https://fasthub-frontend-production.railway.app`

---

### **STEP 6: Update Backend CORS**

**Important!** Backend needs to allow frontend domain.

1. Go back to **"fasthub-backend"** service
2. **"Variables"** tab
3. Update `BACKEND_CORS_ORIGINS`:

```
BACKEND_CORS_ORIGINS=https://fasthub-frontend-production.railway.app
```

**Replace** with **your actual frontend URL** from Step 5.3!

4. Click **"Save"**
5. Backend will auto-redeploy

---

### **STEP 7: Run Database Migrations**

**Option A: Automatic (already configured)**

Migrations run automatically on startup (see `Procfile`).

**Option B: Manual (if needed)**

1. **"fasthub-backend"** service → **"Settings"** → **"Deploy"**
2. **"Custom Start Command":**

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. Click **"Redeploy"**

---

### **STEP 8: Verify Deployment**

#### **Backend:**

1. Open: `https://fasthub-backend-production.railway.app/docs`
2. Should show: **Swagger API documentation** ✅

#### **Frontend:**

1. Open: `https://fasthub-frontend-production.railway.app`
2. Should show: **Login page** ✅

#### **Test Registration:**

1. Click **"Sign up"**
2. Fill 3 fields: Full Name, Email, Password
3. Click **"Create Account"**
4. Should redirect to Dashboard ✅
5. Onboarding modal should appear ✅

---

## 🎉 Success! FastHub is LIVE!

**Your URLs:**
- **Backend:** `https://fasthub-backend-production.railway.app`
- **Frontend:** `https://fasthub-frontend-production.railway.app`
- **API Docs:** `https://fasthub-backend-production.railway.app/docs`

---

## 🔄 Auto-Deploy (Already Working!)

**From now on:**

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push
```

**Railway automatically:**
1. ✅ Detects push to GitHub
2. ✅ Rebuilds Docker images
3. ✅ Deploys new version
4. ✅ **Live in 2-3 minutes!**

**Zero manual deployment!** 🎉

---

## 📊 Monitoring

### **Railway Dashboard shows:**

- ✅ CPU usage
- ✅ Memory usage
- ✅ Request count
- ✅ Deployment history
- ✅ Real-time logs

### **Check regularly:**

1. Is app running?
2. How much credit left? ($5 FREE)
3. Any errors in logs?

---

## 💰 Costs

### **FREE Tier:**

- **$5/month** credit
- **~500h** CPU time
- **~8GB** RAM usage

### **Enough for:**

- ✅ Development/staging
- ✅ MVP with low traffic
- ✅ Testing

### **When $5 runs out:**

- Railway switches to paid plan (~$10-20/month)
- **OR** stops app (if no credit card added)

---

## 🐛 Troubleshooting

### **Error: "Build failed"**

**Solution:**
1. Check Railway logs → Find error
2. Most common: Missing `Dockerfile`
3. Verify: `fasthub-backend/Dockerfile` and `fasthub-frontend/Dockerfile` exist

---

### **Error: "Database connection failed"**

**Solution:**
1. Check `DATABASE_URL` variable
2. Format: `postgresql://user:password@host:5432/database`
3. Verify PostgreSQL service is running

---

### **Error: "CORS policy"**

**Solution:**
1. Backend `BACKEND_CORS_ORIGINS` must include frontend URL
2. Format: `https://your-frontend.railway.app`
3. No trailing slash!

---

### **Frontend can't connect to backend**

**Solution:**
1. Check frontend `VITE_API_URL` variable
2. Must point to backend Railway URL
3. Format: `https://your-backend.railway.app/api/v1`
4. Include `/api/v1` at the end!

---

### **Migrations not running**

**Solution:**
1. Backend service → Settings → Deploy
2. Custom Start Command:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Redeploy

---

## 🔒 Security

### **Environment Variables:**

- ✅ Never commit `.env` files to GitHub
- ✅ Use Railway Variables tab
- ✅ Generate strong `SECRET_KEY` (32+ characters)

### **Database:**

- ✅ Railway PostgreSQL is private (not public)
- ✅ Only backend can access
- ✅ Automatic backups

---

## 🎯 Next Steps

### **1. Custom Domain (Optional)**

1. Railway → Settings → Custom Domain
2. Add: `fasthub.yourdomain.com`
3. Configure DNS (Railway provides instructions)

### **2. Monitoring (Optional)**

1. Add Sentry (error tracking)
2. Railway sends email alerts (when app crashes)

### **3. Scaling (When needed)**

1. Railway → Settings → Resources
2. Increase CPU/RAM
3. Add more replicas

---

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] Backend deployed
- [ ] PostgreSQL added
- [ ] Frontend deployed
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Migrations run
- [ ] Backend `/docs` works
- [ ] Frontend loads
- [ ] Registration tested
- [ ] Auto-deploy verified

---

## 📝 Summary

**What Railway does automatically:**

- ✅ Detects `Dockerfile`
- ✅ Builds Docker images
- ✅ Runs containers
- ✅ Assigns domains
- ✅ Auto-deploys on `git push`
- ✅ Manages PostgreSQL
- ✅ Provides monitoring

**What you did:**

- ✅ Connected GitHub
- ✅ Added environment variables
- ✅ Generated domains

**Time spent:** ~10 minutes

---

**FastHub is now LIVE on Railway!** 🚀

**Share your URLs:**
- Backend: `https://your-backend.railway.app`
- Frontend: `https://your-frontend.railway.app`
