# Docker Deployment Guide for IFix-AI Backend

This guide covers how to build and deploy the IFix-AI backend using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (optional, for using docker-compose)
- Environment variables configured in `.env` file

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f backend
   ```

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t ifix-ai-backend:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name ifix-ai-backend \
     -p 8000:8000 \
     --env-file .env \
     ifix-ai-backend:latest
   ```

3. **View logs:**
   ```bash
   docker logs -f ifix-ai-backend
   ```

4. **Stop and remove the container:**
   ```bash
   docker stop ifix-ai-backend
   docker rm ifix-ai-backend
   ```

## Development Mode

For development with hot reload:

1. **Uncomment the `backend-dev` service in `docker-compose.yml`**

2. **Start development container:**
   ```bash
   docker-compose up backend-dev
   ```

This will mount your source code and enable auto-reload on file changes.

## Building for Production

### Multi-stage Build

The Dockerfile uses multi-stage builds for optimization:

- **builder**: Compiles dependencies
- **production**: Lean runtime image
- **development**: Includes dev tools

### Build specific target:

```bash
# Production (default)
docker build --target production -t ifix-ai-backend:prod .

# Development
docker build --target development -t ifix-ai-backend:dev .
```

## Environment Variables

Ensure your `.env` file contains all required variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
SUPABASE_DB_URL=your_database_url
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key (optional)
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Security Note:** Never commit `.env` file to version control. Use `.env.example` as a template.

## Health Checks

The container includes a health check endpoint:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' ifix-ai-backend

# Manual health check
curl http://localhost:8000/health
```

## Deployment Platforms

### Deploy to AWS ECS

1. **Build and push to ECR:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t ifix-ai-backend .
   docker tag ifix-ai-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ifix-ai-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ifix-ai-backend:latest
   ```

2. **Create ECS task definition and service** using the pushed image

### Deploy to Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ifix-ai-backend

# Deploy to Cloud Run
gcloud run deploy ifix-ai-backend \
  --image gcr.io/PROJECT_ID/ifix-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=xxx,GEMINI_API_KEY=xxx
```

### Deploy to Digital Ocean App Platform

1. Push your code to GitHub
2. Create new app in Digital Ocean
3. Select Docker as the build method
4. Configure environment variables in the dashboard
5. Deploy

### Deploy to Railway

1. Connect your GitHub repository
2. Railway will auto-detect the Dockerfile
3. Configure environment variables
4. Deploy with one click

## Optimization Tips

1. **Layer Caching**: Requirements are copied before source code for better caching
2. **Multi-stage Build**: Reduces final image size by ~60%
3. **Non-root User**: Runs as `appuser` for security
4. **Health Checks**: Automatic container health monitoring
5. **.dockerignore**: Excludes unnecessary files from build context

## Troubleshooting

### Container won't start

1. **Check logs:**
   ```bash
   docker logs ifix-ai-backend
   ```

2. **Verify environment variables:**
   ```bash
   docker exec ifix-ai-backend env | grep SUPABASE
   ```

3. **Run interactive shell:**
   ```bash
   docker exec -it ifix-ai-backend /bin/bash
   ```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Use different port
docker run -p 8001:8000 ifix-ai-backend
```

### Database connection issues

Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correctly set and accessible from the container.

## Image Size Optimization

Current image size is approximately **450-500 MB** (production build).

Further optimization options:
- Use `python:3.11.9-alpine` instead of `slim` (reduces to ~200 MB but may require additional build packages)
- Remove unnecessary dependencies from `requirements.txt`

## Security Best Practices

1. ✅ Runs as non-root user
2. ✅ No secrets in Dockerfile
3. ✅ `.dockerignore` excludes sensitive files
4. ✅ Regular base image updates
5. ✅ Health checks enabled
6. ⚠️ Scan images regularly: `docker scan ifix-ai-backend`

## Monitoring and Logs

### View live logs:
```bash
docker-compose logs -f backend
```

### Export logs:
```bash
docker logs ifix-ai-backend > backend.log 2>&1
```

### Container stats:
```bash
docker stats ifix-ai-backend
```

## Scaling

### Using Docker Compose:
```bash
docker-compose up --scale backend=3
```

### Using Docker Swarm:
```bash
docker service create \
  --name ifix-backend \
  --replicas 3 \
  --publish 8000:8000 \
  ifix-ai-backend:latest
```

## Support

For issues or questions:
- Check container logs first
- Verify environment variables
- Ensure all required services (Supabase) are accessible
- Review FastAPI docs at `http://localhost:8000/docs`
