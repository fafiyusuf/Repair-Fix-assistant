# Deployment Checklist for IFix-AI Backend

## Pre-Deployment

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `SUPABASE_URL` with your Supabase project URL
- [ ] Set `SUPABASE_SERVICE_ROLE_KEY` with your service role key
- [ ] Set `SUPABASE_JWT_SECRET` with your JWT secret
- [ ] Set `SUPABASE_DB_URL` with your database connection string
- [ ] Set `GEMINI_API_KEY` with your Google Gemini API key
- [ ] (Optional) Set `TAVILY_API_KEY` for web search fallback
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `LOG_LEVEL=INFO` (or `WARNING` for production)

### 2. Security Review
- [ ] Ensure `.env` is in `.gitignore` and never committed
- [ ] Verify all API keys are valid and have appropriate permissions
- [ ] Update CORS origins in `app/main.py` to match your frontend URL
- [ ] Review and restrict database access permissions
- [ ] Enable SSL/TLS for database connections in production

### 3. Code Preparation
- [ ] Run linting: `make lint` (if using Makefile)
- [ ] Run tests: `make test` (if tests are available)
- [ ] Commit all changes to version control
- [ ] Tag release version: `git tag -a v1.0.0 -m "Release v1.0.0"`

## Docker Build & Test

### 4. Build Docker Image
- [ ] Build production image: `docker build -t ifix-ai-backend:latest .`
- [ ] Verify image size is reasonable (should be ~450-500 MB)
- [ ] Check for build warnings or errors

### 5. Local Testing
- [ ] Run container locally: `docker run -p 8000:8000 --env-file .env ifix-ai-backend:latest`
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Test API docs: Visit `http://localhost:8000/docs`
- [ ] Test chat endpoint with sample request
- [ ] Check logs for errors: `docker logs <container-id>`
- [ ] Verify database connectivity
- [ ] Test authentication flow

### 6. Performance & Resources
- [ ] Monitor container resource usage: `docker stats`
- [ ] Verify memory usage is within acceptable limits
- [ ] Test under load (optional): Use tools like `ab` or `wrk`
- [ ] Check startup time is reasonable (<60 seconds)

## Deployment Options

### Option A: Docker Compose (Recommended for simple deployments)

#### 7. Deploy with Docker Compose
- [ ] Copy `.env` file to production server
- [ ] Copy `docker-compose.yml` to production server
- [ ] Run: `docker-compose up -d`
- [ ] Verify container is running: `docker-compose ps`
- [ ] Check logs: `docker-compose logs -f backend`

### Option B: Cloud Platform Deployment

#### 8a. AWS ECS/Fargate
- [ ] Create ECR repository
- [ ] Build and push image to ECR
- [ ] Create ECS task definition
- [ ] Configure environment variables in task definition
- [ ] Create ECS service
- [ ] Configure load balancer (ALB)
- [ ] Set up health checks
- [ ] Configure auto-scaling policies

#### 8b. Google Cloud Run
- [ ] Enable Cloud Run API
- [ ] Build and push to GCR/Artifact Registry
- [ ] Deploy to Cloud Run with environment variables
- [ ] Configure minimum/maximum instances
- [ ] Set up custom domain (optional)
- [ ] Enable Cloud Run authentication if needed

#### 8c. Digital Ocean App Platform
- [ ] Connect GitHub repository
- [ ] Configure build settings (Docker)
- [ ] Set environment variables in dashboard
- [ ] Configure health checks
- [ ] Deploy application
- [ ] Set up custom domain (optional)

#### 8d. Railway
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Deploy with one click
- [ ] Monitor deployment logs
- [ ] Set up custom domain (optional)

## Post-Deployment

### 9. Verification
- [ ] Verify health endpoint returns 200: `curl https://your-domain/health`
- [ ] Test API endpoints from frontend
- [ ] Verify authentication works
- [ ] Check database connections are working
- [ ] Test chat functionality end-to-end
- [ ] Verify LLM integration (Gemini) is working

### 10. Monitoring Setup
- [ ] Set up logging aggregation (CloudWatch, Stackdriver, etc.)
- [ ] Configure error tracking (Sentry, optional)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Configure alerts for errors and downtime
- [ ] Monitor API response times
- [ ] Track token usage and costs

### 11. Security Hardening
- [ ] Enable HTTPS/TLS with valid SSL certificate
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Set up rate limiting (if not handled by load balancer)
- [ ] Enable request logging for security audits
- [ ] Regularly scan Docker image for vulnerabilities: `docker scan ifix-ai-backend`
- [ ] Keep base image and dependencies updated

### 12. Documentation
- [ ] Document deployment process for team
- [ ] Create runbook for common issues
- [ ] Document environment variables and their purposes
- [ ] Create rollback procedure
- [ ] Document scaling procedures

## Maintenance

### 13. Regular Updates
- [ ] Schedule regular dependency updates
- [ ] Monitor security advisories
- [ ] Update base Docker image monthly
- [ ] Review and rotate API keys quarterly
- [ ] Backup database regularly (Supabase handles this)

### 14. Scaling Considerations
- [ ] Monitor CPU and memory usage
- [ ] Set up horizontal auto-scaling if needed
- [ ] Consider Redis for session storage (if scaling to multiple instances)
- [ ] Implement database connection pooling if needed
- [ ] Monitor and optimize database queries

## Rollback Plan

### 15. Rollback Procedure
- [ ] Keep previous Docker image tagged
- [ ] Document rollback command: `docker tag ifix-ai-backend:v1.0.0 ifix-ai-backend:latest`
- [ ] Test rollback in staging environment
- [ ] Keep database migration rollback scripts ready

## Quick Commands Reference

### Build & Deploy
```bash
# Build production image
docker build -t ifix-ai-backend:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Troubleshooting
```bash
# Check container status
docker ps -a

# View logs
docker logs <container-id>

# Execute shell in container
docker exec -it <container-id> /bin/bash

# Check health
curl http://localhost:8000/health

# View resource usage
docker stats
```

### Using Makefile (if available)
```bash
make build      # Build image
make run        # Run container
make logs       # View logs
make stop       # Stop container
make clean      # Clean up
make health     # Check health
```

## Support & Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Docker Documentation**: https://docs.docker.com/
- **Supabase Documentation**: https://supabase.com/docs
- **LangChain Documentation**: https://python.langchain.com/

## Notes

- Always test in a staging environment before production deployment
- Keep `.env` file secure and never commit to version control
- Monitor costs associated with API usage (Gemini, Tavily)
- Regularly review logs for errors and performance issues
- Keep this checklist updated with your specific deployment process
