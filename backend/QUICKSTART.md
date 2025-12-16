# 🚀 IFix-AI Backend Docker - Quick Reference

## One-Command Deploy

```bash
./deploy.sh
```
Then select option 1.

---

## Essential Commands

### Build & Run
```bash
# Docker Compose (easiest)
docker-compose up -d

# Docker CLI
docker build -t ifix-ai-backend:latest .
docker run -d -p 8000:8000 --env-file .env ifix-ai-backend:latest

# Makefile
make build run
```

### Monitor
```bash
# Logs
docker-compose logs -f backend
# or
docker logs -f ifix-ai-backend

# Health
curl http://localhost:8000/health

# Stats
docker stats ifix-ai-backend
```

### Stop
```bash
# Docker Compose
docker-compose down

# Docker CLI
docker stop ifix-ai-backend
```

---

## Environment Setup

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required variables:**
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_DB_URL`
- `GEMINI_API_KEY`

---

## URLs

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## Troubleshooting

```bash
# View logs
docker logs ifix-ai-backend

# Check container status
docker ps -a

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Shell access
docker exec -it ifix-ai-backend /bin/bash
```

---

## Development Mode

```bash
# With hot reload
docker-compose up backend-dev
```

---

## Production Deploy

See full guides:
- **README.Docker.md** - Platform-specific instructions
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment

---

## Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build config |
| `docker-compose.yml` | Service orchestration |
| `.dockerignore` | Build optimization |
| `deploy.sh` | Interactive deployment |
| `Makefile` | Command shortcuts |
| `.env` | Environment config (don't commit!) |

---

## Quick Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"IFix-AI Backend","version":"1.0.0"}
```

---

**Need help?** Check `DOCKER_SUMMARY.md` for complete overview.
