# Docker Deployment Guide

## Quick Start (Development)

### 1. Start all services
```bash
docker-compose up -d
```

This will start:
- **FastAPI API** (port 8000)
- **MySQL database** (port 3306)
- **Redis cache** (port 6379)
- **Adminer** (port 8080) - Database management UI

### 2. Run database migrations
```bash
docker-compose exec api alembic upgrade head
```

### 3. Access services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer: http://localhost:8080 (server: db, user: autoflow, password: autoflow_password)

### 4. View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

### 5. Stop services
```bash
docker-compose down
```

---

## Production Deployment

### 1. Set environment variables
Create `.env.prod` file:
```env
# Database (use external managed database)
DATABASE_URL=mysql+aiomysql://user:password@host:3306/database

# Security
SECRET_KEY=your-super-secret-key-change-this

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=your-redis-password

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Frontend
FRONTEND_URL=https://yourdomain.com
```

### 2. Generate SSL certificates
```bash
# Using Let's Encrypt (certbot)
certbot certonly --standalone -d yourdomain.com

# Copy certificates
mkdir ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
```

### 3. Start production services
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 4. Run migrations
```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 5. Scale API instances
```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

## Docker Commands Cheat Sheet

### Build & Start
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build
```

### Manage Services
```bash
# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove containers
docker-compose down

# Remove containers + volumes
docker-compose down -v
```

### Logs & Debugging
```bash
# View logs
docker-compose logs -f [service]

# Execute command in container
docker-compose exec api bash

# Check service status
docker-compose ps
```

### Database Operations
```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Access MySQL shell
docker-compose exec db mysql -u autoflow -p autoflow
```

### Cleanup
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything
docker system prune -a --volumes
```

---

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database connection failed
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Permission denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Out of disk space
```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

---

## Health Checks

All services have health checks configured:

- **API**: `GET /api/v1/health`
- **Database**: `mysqladmin ping`
- **Redis**: `redis-cli ping`

Check health status:
```bash
docker-compose ps
```

---

## Monitoring

### View resource usage
```bash
docker stats
```

### View container logs
```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from specific time
docker-compose logs --since 2024-01-01T00:00:00
```

---

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use strong SECRET_KEY** - Generate with `openssl rand -hex 32`
3. **Change default passwords** - Especially for production
4. **Use SSL/TLS** - Always in production
5. **Keep images updated** - Regularly update base images
6. **Scan for vulnerabilities** - Use `docker scan`
7. **Limit container resources** - Set CPU/memory limits
8. **Use non-root user** - Already configured in Dockerfile

---

## Performance Optimization

1. **Multi-stage builds** - Reduces image size (already implemented)
2. **Layer caching** - Order Dockerfile commands by change frequency
3. **Use .dockerignore** - Exclude unnecessary files
4. **Enable gzip** - Configured in nginx
5. **Connection pooling** - SQLAlchemy already configured
6. **Redis caching** - Use for frequently accessed data

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t autoflow-api .
      
      - name: Push to registry
        run: docker push autoflow-api
      
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && docker-compose pull && docker-compose up -d'
```

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Verify environment variables: `docker-compose config`
- Restart services: `docker-compose restart`
- Check Docker documentation: https://docs.docker.com
