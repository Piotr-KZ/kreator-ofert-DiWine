# 🚀 Railway Deployment Guide (CORRECTED)

## ⚠️ Important Note

**Railway does NOT support `docker-compose.yml` directly.**

**Solution:** Deploy 3 separate services:
1. Backend (from `fasthub-backend/`)
2. Frontend (from `fasthub-frontend/`)
3. PostgreSQL (managed database)

---

## 📋 Overview

Deploy FastHub to Railway in **15 minutes** with automatic CI/CD from GitHub.

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

### **STEP 2: Remove Failed Deployment (if exists)**

If you already tried to deploy and it failed:

1. Railway Dashboard → Your project
2. Click **"..."** (3 dots menu)
3. **"Remove Service"**
4. Confirm

---

### **STEP 3: Deploy Backend**

#### **3.1. Create Backend Service:**

1. Railway Dashboard → **"+ New"**
2. Choose: **"GitHub Repo"**
3. Select: **`Fasthub`** repository
4. **IMPORTANT:** Click **"Configure"** (before deploy)
5. Set **"Root Directory"**: `fasthub-backend`
6. Set **"Builder"**: `Dockerfile`
7. Click **"Deploy"**

Railway will:
- ✅ Detect `fasthub-backend/Dockerfile`
- ✅ Build Docker image
- ✅ Deploy backend

**Wait 3-5 minutes** for build + deploy.

---

### **STEP 4: Add PostgreSQL Database**

1. In the same project → **"+ New"**
2. Choose: **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically:
   - ✅ Create database
   - ✅ Set `DATABASE_URL` variable in backend

**That's it!** Database is ready.

---

### **STEP 5: Configure Backend Environment Variables**

1. Click on **"backend"** service
2. Go to **"Variables"** tab
3. Railway already added `DATABASE_URL` ✅

**Add manually:**

```
SECRET_KEY=<generate-random-32-character-string>
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

# Option 3: Online
# Use: https://randomkeygen.com/ (256-bit key)
```

4. Click **"Add"** for each variable
5. Railway will auto-redeploy

---

### **STEP 6: Run Database Migrations**

Backend needs to run migrations before starting:

1. **"backend"** service → **"Settings"**
2. Scroll to **"Deploy"** section
3. **"Custom Start Command"**:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Click **"Save"**
5. Railway will redeploy

**Migrations will run automatically** before backend starts ✅

---

### **STEP 7: Generate Backend Domain**

1. **"backend"** service → **"Settings"**
2. **"Networking"** → **"Generate Domain"**
3. Copy URL: `https://fasthub-backend-production-xxx.up.railway.app`

**⚠️ SAVE THIS URL!** You'll need it for frontend.

---

### **STEP 8: Deploy Frontend**

#### **8.1. Create Frontend Service:**

1. In the project → **"+ New"**
2. **"GitHub Repo"**
3. Select: **`Fasthub`** (same repo!)
4. Click **"Configure"**
5. Set **"Root Directory"**: `fasthub-frontend`
6. Set **"Builder"**: `Dockerfile`

#### **8.2. Add Frontend Environment Variables:**

Before clicking "Deploy", go to **"Variables"** tab:

```
VITE_API_URL=https://[BACKEND-URL-FROM-STEP-7]/api/v1
```

**⚠️ Replace `[BACKEND-URL-FROM-STEP-7]`** with your actual backend URL!

**Example:**
```
VITE_API_URL=https://fasthub-backend-production-abc123.up.railway.app/api/v1
```

7. Click **"Deploy"**

Railway will build frontend with `fasthub-frontend/Dockerfile` ✅

---

### **STEP 9: Generate Frontend Domain**

1. **"frontend"** service → **"Settings"**
2. **"Networking"** → **"Generate Domain"**
3. Copy URL: `https://fasthub-frontend-production-xxx.up.railway.app`

**⚠️ SAVE THIS URL!** You'll need it for CORS.

---

### **STEP 10: Update Backend CORS**

Backend must accept requests from frontend:

1. Go back to **"backend"** service
2. **"Variables"** tab
3. Add:

```
BACKEND_CORS_ORIGINS=https://[FRONTEND-URL-FROM-STEP-9]
```

**⚠️ Replace `[FRONTEND-URL-FROM-STEP-9]`** with your actual frontend URL!

**Example:**
```
BACKEND_CORS_ORIGINS=https://fasthub-frontend-production-xyz789.up.railway.app
```

4. Click **"Add"**
5. Railway will auto-redeploy backend

---

### **STEP 11: Verify Deployment**

#### **Frontend:**

1. Open: `https://[your-frontend-url].up.railway.app`
2. Should show: **Login page** ✅

#### **Backend API:**

1. Open: `https://[your-backend-url].up.railway.app/docs`
2. Should show: **Swagger API documentation** ✅

#### **Test Registration:**

1. Go to frontend → Click **"Sign up"**
2. Fill 3 fields: Full Name, Email, Password
3. Click **"Create Account"**
4. Should redirect to Dashboard ✅
5. Onboarding modal should appear ✅

---

## 🎉 Success! FastHub is LIVE!

**Your URLs:**
- **Backend:** `https://fasthub-backend-production-xxx.up.railway.app`
- **Frontend:** `https://fasthub-frontend-production-xxx.up.railway.app`
- **API Docs:** `https://fasthub-backend-production-xxx.up.railway.app/docs`

---

## 📊 Railway Project Structure

```
Railway Project: Fasthub
├─ Service: backend
│  └─ Source: github.com/Piotr-KZ/Fasthub/fasthub-backend
│  └─ Dockerfile: fasthub-backend/Dockerfile
│
├─ Service: frontend
│  └─ Source: github.com/Piotr-KZ/Fasthub/fasthub-frontend
│  └─ Dockerfile: fasthub-frontend/Dockerfile
│
└─ Database: PostgreSQL
   └─ Auto-connected to backend (DATABASE_URL)
```

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
2. ✅ Rebuilds backend + frontend Docker images
3. ✅ Deploys new versions
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

### **Error: "No Dockerfile found"**

**Solution:**
1. Check **"Root Directory"** in service Settings
2. Backend: `fasthub-backend`
3. Frontend: `fasthub-frontend`

---

### **Error: "Database connection failed"**

**Solution:**
1. Check `DATABASE_URL` variable in backend
2. Railway should auto-set this when you add PostgreSQL
3. Format: `postgresql://user:password@host:5432/database`
4. Verify PostgreSQL service is running

---

### **Error: "Migrations failed"**

**Solution:**
1. Backend service → Settings → Deploy
2. Custom Start Command:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Check logs for migration errors

---

### **Frontend: "Network Error" / "API not responding"**

**Solution:**
1. Check frontend `VITE_API_URL` variable
2. Must point to backend Railway URL
3. Format: `https://your-backend.up.railway.app/api/v1`
4. Include `/api/v1` at the end!
5. Check if backend is running: `https://[backend-url]/health`

---

### **Error: "CORS policy"**

**Solution:**
1. Backend `BACKEND_CORS_ORIGINS` must include frontend URL
2. Format: `https://your-frontend.up.railway.app`
3. No trailing slash!
4. Exact match required

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
- [ ] Backend service deployed (Root Directory: `fasthub-backend`)
- [ ] PostgreSQL added
- [ ] Backend environment variables set (SECRET_KEY, ENVIRONMENT)
- [ ] Database migrations configured (Custom Start Command)
- [ ] Backend domain generated
- [ ] Frontend service deployed (Root Directory: `fasthub-frontend`)
- [ ] Frontend environment variables set (VITE_API_URL)
- [ ] Frontend domain generated
- [ ] Backend CORS configured (BACKEND_CORS_ORIGINS)
- [ ] Backend `/docs` works
- [ ] Frontend loads
- [ ] Registration tested
- [ ] Auto-deploy verified

---

## 📝 Summary

**What Railway does automatically:**

- ✅ Detects `Dockerfile` in root directory
- ✅ Builds Docker images
- ✅ Runs containers
- ✅ Assigns domains
- ✅ Auto-deploys on `git push`
- ✅ Manages PostgreSQL
- ✅ Provides monitoring

**What you did:**

- ✅ Deployed backend (from `fasthub-backend/`)
- ✅ Deployed frontend (from `fasthub-frontend/`)
- ✅ Added PostgreSQL
- ✅ Configured environment variables
- ✅ Set up CORS
- ✅ Generated domains

**Time spent:** ~15 minutes

---

**FastHub is now LIVE on Railway!** 🚀

**Share your URLs:**
- Backend: `https://your-backend.up.railway.app`
- Frontend: `https://your-frontend.up.railway.app`
