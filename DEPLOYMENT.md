# 🚀 AisleIQ Deployment Guide

This guide covers deploying **AisleIQ** (FastAPI Backend, PostgreSQL Database, and React/Vite Frontend) to managed cloud platforms.

### 🌐 Live Production Deployment
- **Live Frontend Dashboard:** [https://aisle-iq-dashboard.vercel.app](https://aisle-iq-dashboard.vercel.app)
- **Live Backend API:** [https://aisle-iq-api.onrender.com](https://aisle-iq-api.onrender.com)
- **Interactive Swagger Docs:** [https://aisle-iq-api.onrender.com/docs](https://aisle-iq-api.onrender.com/docs)
- **Database:** Managed PostgreSQL on Supabase

---

## 🏛️ Deployment Architecture

```
                    ┌─────────────────────────┐
                    │    React Frontend       │
                    │ (Vercel / Render Static)│
                    └───────────┬─────────────┘
                                │ HTTPS Requests
                                ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │  (Render / Railway /    │
                    │      Cloud VM)          │
                    └───────▲───────────┬─────┘
                            │           │
     Live Ingestion Events  │           │ Asyncpg Queries
(pipeline/detect.py / Edge) │           ▼
                            │ ┌───────────────────┐
                            │ │   PostgreSQL DB   │
                            │ │ (Render/Supabase) │
                            │ └───────────────────┘
```

---

## 🌟 Option 1: Render (Recommended — 1-Click Blueprint)

A complete [`render.yaml`](./render.yaml) blueprint is included in the root directory. It automatically sets up:
1. **Managed PostgreSQL Database** (`aisleiq-db`)
2. **FastAPI Web Service** (`aisleiq-api`) with automatic Alembic migrations
3. **Vite React Static Site** (`aisleiq-frontend`) with SPA routing and API connection

### Steps:
1. **Push your code** to GitHub or GitLab:
   ```bash
   git add .
   git commit -m "Configure deployment files"
   git push origin main
   ```
2. Log into [Render](https://dashboard.render.com/).
3. Click **"New +"** ➔ **"Blueprint"**.
4. Connect your AisleIQ repository.
5. Render will automatically read `render.yaml` and provision:
   - Database: `aisleiq-db`
   - Backend: `aisleiq-api`
   - Frontend: `aisleiq-frontend`
6. Click **"Apply"**. Once deployed, Render will provide live URLs for both your backend and frontend.

---

## ⚡ Option 2: Split Deployment (Vercel Frontend + Render/Railway API + Supabase DB)

### 1. Database (Supabase or Neon)
1. Create a free PostgreSQL instance on [Supabase](https://supabase.com) or [Neon](https://neon.tech).
2. Copy the Connection URI (`postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`).

### 2. Backend (Render or Railway)
1. In Render or Railway, create a **New Web Service** connected to your repository.
2. Configure:
   - **Root Directory:** `.` (root)
   - **Runtime / Environment:** `Python 3.11`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
3. Add Environment Variable:
   - `DATABASE_URL`: Your Supabase/Neon PostgreSQL URI (e.g. `postgresql://...`)
4. Deploy the service and note the API URL (e.g. `https://aisleiq-api.onrender.com`).

### 3. Frontend (Vercel)
1. Go to [Vercel](https://vercel.com) and click **"Add New Project"**.
2. Select your repository.
3. Configure:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. In **Environment Variables**, add:
   - `VITE_API_URL`: `https://your-backend-api-url.onrender.com`
5. Click **"Deploy"**. Vercel will build the frontend using `frontend/vercel.json` SPA rewrite rules.

---

## 🐳 Option 3: Single Cloud VM / VPS (AWS EC2 / DigitalOcean Droplet)

If you prefer self-hosting with Docker Compose:

1. SSH into your VPS (Ubuntu 22.04+ recommended) and install Docker & Docker Compose:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-plugin
   ```
2. Clone your repository:
   ```bash
   git clone https://github.com/keesha-luthra/aisle-iq.git
   cd aisle-iq
   ```
3. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```
4. Start the stack:
   ```bash
   docker compose up -d --build
   ```
5. Access:
   - **Frontend:** `http://<YOUR_SERVER_IP>`
   - **Backend API Docs:** `http://<YOUR_SERVER_IP>:8000/docs`
   - **Health Check:** `http://<YOUR_SERVER_IP>:8000/health`

---

## 📹 Running the Detection Pipeline with Cloud Backend

The heavy computer vision and object detection pipeline (`pipeline/detect.py`) runs locally on your host or edge camera server and streams detection events directly to your deployed cloud backend.

Run the pipeline and ingestion pointing to your live cloud URL:

```bash
python scripts/run_pipeline_and_ingest.py \
  --clips-dir ./data/clips \
  --store-id STORE_BLR_002 \
  --api-url https://your-backend-api-url.onrender.com
```

---

## 🧪 Post-Deployment Verification

Verify your deployment is functioning properly:

1. **API Health Check:**
   ```bash
   curl https://your-backend-api-url.onrender.com/health
   # Expected: {"status":"healthy","database":"connected",...}
   ```
2. **Interactive Swagger Docs:**
   Visit `https://your-backend-api-url.onrender.com/docs` in your browser.
3. **Frontend Dashboard:**
   Open your frontend URL (e.g. `https://aisleiq.vercel.app` or `https://aisleiq-frontend.onrender.com`).
   - Store selector should load available stores (`STORE_BLR_002`, `STORE_MUM_076`).
   - Metrics, Heatmap, and Funnel analytics should render live data.
