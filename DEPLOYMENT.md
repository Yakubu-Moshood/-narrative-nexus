# 🚀 Narrative Nexus Deployment Guide

Complete instructions for deploying Narrative Nexus to production environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Streamlit Sharing (Free)](#streamlit-sharing-free)
3. [Heroku](#heroku)
4. [Docker](#docker)
5. [AWS](#aws)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Setup

```bash
# Clone repository
git clone <repository-url>
cd narrative-nexus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Development Tips
- Edit `app.py` and Streamlit auto-reloads
- Use `streamlit run app.py --logger.level=debug` for debugging
- Check `.streamlit/config.toml` for theme customization

---

## Streamlit Sharing (Free)

**Pros**: Free, easy, no infrastructure management  
**Cons**: Limited resources, public repository required

### Steps

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/narrative-nexus.git
   git branch -M main
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Sign in with GitHub**

4. **Click "New app"**

5. **Fill in details**:
   - Repository: `YOUR_USERNAME/narrative-nexus`
   - Branch: `main`
   - File path: `app.py`

6. **Click "Deploy"**

7. **Share your link**: `https://share.streamlit.io/YOUR_USERNAME/narrative-nexus`

### Limitations
- 1 GB memory limit
- Runs on shared infrastructure
- Public repository only

---

## Heroku

**Pros**: Easy deployment, good for small apps, free tier available  
**Cons**: Slower startup, limited free tier resources

### Prerequisites
- Heroku account (free at [heroku.com](https://www.heroku.com))
- Heroku CLI installed

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create narrative-nexus-YOUR_NAME
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **View logs**
   ```bash
   heroku logs --tail
   ```

5. **Open app**
   ```bash
   heroku open
   ```

### Configuration

The `Procfile` and `.streamlit/config.toml` are already configured. If needed, adjust:

```bash
# Set environment variables
heroku config:set SOME_VAR=value

# View config
heroku config
```

### Scaling
```bash
# View dyno types
heroku dyno:type

# Upgrade dyno (paid)
heroku dyno:upgrade standard-1x
```

---

## Docker

**Pros**: Consistent environment, portable, scalable  
**Cons**: Requires Docker knowledge

### Build & Run Locally

```bash
# Build image
docker build -t narrative-nexus:latest .

# Run container
docker run -p 8501:8501 narrative-nexus:latest

# Access at http://localhost:8501
```

### Deploy to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag narrative-nexus:latest YOUR_USERNAME/narrative-nexus:latest

# Push
docker push YOUR_USERNAME/narrative-nexus:latest
```

### Deploy to AWS ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name narrative-nexus

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag narrative-nexus:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/narrative-nexus:latest

# Push
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/narrative-nexus:latest
```

---

## AWS

### Option 1: AWS App Runner (Easiest)

```bash
# Create service from Docker image
aws apprunner create-service \
  --service-name narrative-nexus \
  --source-configuration ImageRepository={ImageIdentifier=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/narrative-nexus:latest,ImageRepositoryType=ECR}
```

### Option 2: ECS Fargate

1. Create ECS cluster
2. Create task definition with Docker image
3. Create service
4. Configure load balancer
5. Deploy

### Option 3: Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker narrative-nexus

# Create environment
eb create narrative-nexus-env

# Deploy
eb deploy

# Open app
eb open
```

---

## Performance Optimization

### Caching
```python
@st.cache_resource
def load_model():
    # Load transformers model once
    return pipeline("sentiment-analysis")
```

### Session State
```python
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
```

### Reduce Model Size
- Use `distilbert` instead of `bert` (smaller, faster)
- Cache model downloads
- Consider CPU-only inference

### Memory Management
```bash
# Limit memory usage
streamlit run app.py --logger.level=error --client.maxMessageSize=200
```

---

## Monitoring & Logging

### Streamlit Cloud
- Built-in logs at `https://share.streamlit.io/YOUR_USERNAME/narrative-nexus`

### Heroku
```bash
heroku logs --tail
heroku logs --num 100
```

### Docker
```bash
docker logs <container_id>
docker logs -f <container_id>  # Follow logs
```

### AWS CloudWatch
```bash
# View logs
aws logs tail /aws/apprunner/narrative-nexus --follow
```

---

## Security Checklist

- [ ] No API keys in code (use environment variables)
- [ ] HTTPS enabled (automatic on Streamlit Sharing, Heroku, AWS)
- [ ] Input validation (already implemented)
- [ ] File size limits (already set: 10MB text, 50MB CSV)
- [ ] Rate limiting (consider for production)
- [ ] Authentication (consider for future versions)

---

## Troubleshooting

### App crashes on startup
```bash
# Check logs
streamlit run app.py --logger.level=debug

# Verify dependencies
pip install -r requirements.txt --upgrade
```

### Slow sentiment analysis
- First run downloads model (~300MB)
- Subsequent runs use cache
- Consider using CPU-only: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

### Memory issues
- Reduce simulation runs (100 is default)
- Process CSV in chunks
- Use streaming for large files

### Model download fails
```bash
# Pre-download model
python -c "from transformers import pipeline; pipeline('sentiment-analysis')"
```

### Port already in use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

---

## Scaling for Production

### Load Balancing
- Use AWS ELB or Heroku's built-in load balancing
- Scale horizontally with multiple instances

### Caching
- Implement Redis for session caching
- Cache model predictions
- Use CDN for static assets

### Database
- Add PostgreSQL for user accounts (future feature)
- Store analysis history
- Track usage metrics

### Monitoring
- Set up CloudWatch alarms
- Monitor CPU, memory, latency
- Alert on errors

---

## Cost Estimation

| Platform | Free Tier | Paid (Monthly) |
|----------|-----------|----------------|
| Streamlit Sharing | ✅ Unlimited | N/A |
| Heroku | ✅ 550 hours | $7+ |
| AWS App Runner | ❌ | $0.065/hour |
| AWS ECS | ❌ | $0.10+/hour |
| Docker Hub | ✅ 1 private repo | $5+ |

---

## Next Steps

1. **Test locally**: `streamlit run app.py`
2. **Choose platform**: Streamlit Sharing (easiest), Heroku (good balance), Docker (most control)
3. **Deploy**: Follow platform-specific steps above
4. **Monitor**: Check logs and performance
5. **Iterate**: Gather feedback and improve

---

For questions or issues, see [README.md](README.md) or create a GitHub issue.
