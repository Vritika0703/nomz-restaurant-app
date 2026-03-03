# AWS Deployment Guide for Team3 Nomz Project

## Overview
This guide explains how to deploy your Django application to AWS using Elastic Beanstalk with RDS PostgreSQL database and S3 for static files.

## What You Need

### 1. **AWS Account & CLI Setup**
- AWS Account with appropriate permissions
- AWS CLI installed locally
- EB CLI (Elastic Beanstalk CLI) installed

```bash
pip install awsebcli
```

### 2. **Git Production Branch**
Ensure your `production` branch is ready in GitHub:
```bash
git checkout -b production
git push origin production
```

---

## Pre-Deployment Checklist

### ✅ Code Changes (Already Done)
- [x] Updated `requirements.txt` with AWS dependencies (gunicorn, boto3, django-storages, whitenoise)
- [x] Created `.env.example` with all required environment variables
- [x] Updated `settings.py` for production deployment
- [x] Created `Procfile` for process management
- [x] Created `.ebextensions/` for AWS Elastic Beanstalk configuration
- [x] Created `runtime.txt` specifying Python 3.11.8

### 📋 Local Testing (YOU SHOULD DO THIS)
Before deploying to AWS:

```bash
# 1. Create a local .env file (copy from .env.example)
cp .env.example .env

# 2. Set DEBUG=True locally for testing
# 3. Test with PostgreSQL locally (optional but recommended)
# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Test with gunicorn locally
gunicorn restaurants.wsgi:application --bind 0.0.0.0:8000
```

---

## Step-by-Step AWS Deployment

### Step 1: Create AWS RDS PostgreSQL Database

1. Go to **RDS Console** → **Create Database**
2. Choose **PostgreSQL** → **Free tier eligible** (if applicable)
3. **Settings:**
   - DB Instance Identifier: `nomz-db`
   - Master username: `postgres`
   - Master password: **(SECURE PASSWORD)**
   - Initial database name: `nomz_db`
4. **Connectivity:**
   - Public accessibility: Yes (so EB can connect)
   - VPC Security Group: Create new or configure existing
5. Create database and note down the **Endpoint** (e.g., `nomz-db.c12k9jd4k2.us-east-1.rds.amazonaws.com`)

### Step 2: Create AWS S3 Bucket for Static Files

1. Go to **S3 Console** → **Create Bucket**
2. **Bucket name**: `nomz-static-files` (must be globally unique)
3. **Region**: Same as your EB environment
4. **Permissions:**
   - Block all public access: **OFF** (allow public reads for static files)
5. Create bucket
6. Configure **Bucket Policy** to allow public read access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nomz-static-files/*"
        }
    ]
}
```

### Step 3: Create IAM User for Application Access

1. Go to **IAM Console** → **Users** → **Create User**
2. **User name**: `nomz-app`
3. Attach policies:
   - `AmazonS3FullAccess` (for S3 access)
4. Create **Access Key**:
   - Save **Access Key ID** and **Secret Access Key**

### Step 4: Initialize Elastic Beanstalk

```bash
# Navigate to your project directory
cd team3-mon-spring26

# Initialize EB (first time only)
eb init -p python-3.11 nomz-production --region us-east-1

# Create environment
eb create nomz-prod --instance-type t3.micro --scale 1
```

### Step 5: Configure Environment Variables in AWS

Set environment variables in Elastic Beanstalk:

```bash
eb setenv \
  ENVIRONMENT=production \
  DEBUG=False \
  SECRET_KEY=your-secure-secret-key-here \
  ALLOWED_HOSTS=your-domain.com,www.your-domain.com \
  DB_ENGINE=django.db.backends.postgresql \
  DB_NAME=nomz_db \
  DB_USER=postgres \
  DB_PASSWORD=your-secure-password \
  DB_HOST=nomz-db.c12k9jd4k2.us-east-1.rds.amazonaws.com \
  DB_PORT=5432 \
  USE_S3=True \
  AWS_ACCESS_KEY_ID=your-access-key-id \
  AWS_SECRET_ACCESS_KEY=your-secret-access-key \
  AWS_STORAGE_BUCKET_NAME=nomz-static-files \
  AWS_S3_REGION_NAME=us-east-1 \
  CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Replace placeholders with actual values.

### Step 6: Deploy to AWS

```bash
# Deploy from production branch
git checkout production
git pull origin production

# Deploy with EB
eb deploy

# Monitor deployment
eb logs
```

### Step 7: Connect Production Branch to Auto-Deploy (CI/CD)

To auto-deploy when you push to GitHub production branch:

1. **In AWS Web Console**:
   - Go to **CodePipeline** → **Create Pipeline**
   - Source: GitHub
   - Branch: `production`
   - Deploy provider: AWS Elastic Beanstalk
   
2. **Or use GitHub Actions** (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to Elastic Beanstalk
        run: |
          eb deploy nomz-prod --verbose
```

---

## After Deployment

### 1. Run Migrations
```bash
eb ssh
python manage.py migrate
python manage.py createsuperuser
exit
```

### 2. Collect Static Files (if needed)
```bash
python manage.py collectstatic --noinput
```

### 3. Configure Domain Name
- Update Route 53 or your domain registrar DNS to point to EB domain
- Or configure custom domain: `eb scale 1` → AWS EB Console → Domain management

### 4. Enable HTTPS with AWS Certificate Manager
1. Request SSL certificate for your domain
2. Apply to ALB in EB console

---

## Important Environment Variables Checklist

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `SECRET_KEY` | Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` | Generate locally |
| `DB_HOST` | RDS endpoint | AWS RDS Console |
| `DB_PASSWORD` | Your secure password | AWS RDS Setup |
| `AWS_ACCESS_KEY_ID` | IAM User access key | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | IAM User secret | AWS IAM Console |
| `AWS_STORAGE_BUCKET_NAME` | Your S3 bucket name | AWS S3 Console |

---

## Troubleshooting

### Deployment Fails
```bash
eb logs
# Check the last 100 lines for errors
```

### Database Connection Error
- Ensure RDS security group allows inbound traffic on port 5432 from EB instances
- Check DB credentials in environment variables

### Static Files Not Loading
- Ensure S3 bucket exists and is public
- Verify AWS credentials have S3 permissions
- Run `python manage.py collectstatic --noinput` 

### Missing Dependencies
- Ensure all packages are in `requirements.txt`
- Run locally: `pip freeze > requirements.txt`

---

## Next Steps

1. ✅ Update code (DONE)
2. ✅ Create RDS database
3. ✅ Create S3 bucket
4. ✅ Create IAM user
5. ✅ Initialize & deploy EB
6. ✅ Set environment variables
7. ✅ Run migrations
8. ✅ Configure auto-deployment from production branch

---

**Need Help?**
- AWS EB Documentation: https://docs.aws.amazon.com/elasticbeanstalk/
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
- django-storages (S3): https://django-storages.readthedocs.io/
