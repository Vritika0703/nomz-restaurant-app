# Phase 2: AWS Elastic Beanstalk Deployment Guide

Complete step-by-step instructions to deploy your Django application to AWS Elastic Beanstalk with auto-deployment from your GitHub production branch.

---

## Prerequisites

Before starting Phase 2, verify you have:

- ✅ Phase 1 complete (RDS, S3, IAM user created)
- ✅ `.env` file configured with all credentials
- ✅ GitHub repository with `production` branch
- ✅ AWS Account access
- ✅ Code changes committed to Git

---

## Part A: Install Required Tools

### Step 1: Install AWS CLI

On Windows PowerShell (as Administrator):

```powershell
# Install AWS CLI
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

Or if you prefer, download from: https://aws.amazon.com/cli/

### Step 2: Verify AWS CLI Installation

```powershell
aws --version
```

You should see:
```
aws-cli/2.x.xx
```

### Step 3: Install Elastic Beanstalk CLI (EB CLI)

```powershell
pip install awsebcli
```

### Step 4: Verify EB CLI Installation

```powershell
eb --version
```

You should see:
```
EB CLI 3.x.xx
```

---

## Part B: Configure AWS Credentials

### Step 1: Get Your AWS Access Keys

If you haven't saved your AWS account credentials from Phase 1:

1. Go to AWS Console → IAM → Users
2. Click on your **root account** or **admin user**
3. Go to **Security credentials** tab
4. Create new access key if needed
5. **Save:**
   - Access Key ID
   - Secret Access Key

### Step 2: Configure AWS CLI

In PowerShell, run:

```powershell
aws configure
```

You'll be prompted for:

```
AWS Access Key ID [None]: AKIAI...    ← Paste your Access Key ID
AWS Secret Access Key [None]: wJalr...  ← Paste your Secret Access Key
Default region name [None]: us-east-1
Default output format [None]: json
```

Just press Enter for region and output (use defaults).

### Step 3: Verify Configuration

```powershell
aws sts get-caller-identity
```

You should see your AWS account info:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/..."
}
```

---

## Part C: Prepare Your Git Repository

### Step 1: Create/Checkout Production Branch

```powershell
cd c:\Users\darsh\OneDrive\Desktop\MS\ -\ acads\CSGY\ 6063\ -\ Software\ Engineering\ I\team3-mon-spring26

# Check current branch
git branch

# Create production branch if it doesn't exist
git checkout -b production

# Or checkout if it exists
git checkout production
```

### Step 2: Commit Your Changes

Make sure all code changes (including the files we created) are committed:

```powershell
git add .
git commit -m "Add AWS deployment configuration and environment variables setup"
```

### Step 3: Push to GitHub

```powershell
git push origin production
```

---

## Part D: Initialize Elastic Beanstalk Environment

### Step 1: Navigate to Project Directory

```powershell
cd "C:\Users\darsh\OneDrive\Desktop\MS - acads\CSGY 6063 - Software Engineering I\team3-mon-spring26"
```

### Step 2: Initialize EB Application

```powershell
eb init
```

You'll be prompted with questions:

```
Select a default region
1) us-east-1 : US East (N. Virginia)
2) us-west-2 : US West (Oregon)
...
(3 more choices)
Select default region: 1    ← Select us-east-1 (same as RDS)

Select an application to use
[ Create new Application ]
(if you have existing apps)
(1) [ Create new Application ]

Type the Application Name
(default is "team3-mon-spring26"): nomz-production   ← Name your app

It appears you are using Python. Is this correct?
(Y/n): Y    ← Press Y

Select a Python version to use
1) Python 3.11 running on 64bit Amazon Linux 2023.09.3
2) Python 3.12 running on 64bit Amazon Linux 2023.09.3
...
(1) [ Create new Application ]: 1    ← Select Python 3.11
```

### Step 3: Verify Initialization

Check that `.elasticbeanstalk/config.yml` was created:

```powershell
ls .elasticbeanstalk/
```

You should see:
```
config.yml
```

---

## Part E: Create Elastic Beanstalk Environment

### Step 1: Create Environment

```powershell
eb create nomz-prod --instance-type t3.micro --envvars ENVIRONMENT=production,DEBUG=False
```

This will:
- Create an environment named: `nomz-prod`
- Use t3.micro instance (free tier eligible)
- Set environment variables

**This takes 10-15 minutes.** Monitor progress:

```
Creating application version archive "app-...".
Uploading app-....zip to S3.
Environment creation starting.
  ...
  Environment nomz-prod has been created.
  Endpoint: nomz-prod.us-east-1.elasticbeanstalk.com
```

### Step 2: Check Environment Status

```powershell
eb status
```

Wait for:
```
Environment Details
  ...
  Status: Ready
  Health: Green
```

---

## Part F: Set Environment Variables in AWS EB

Your `.env` file is local only. You need to set variables in AWS:

### Step 1: Set All Environment Variables

```powershell
eb setenv `
  DEBUG=False `
  ENVIRONMENT=production `
  SECRET_KEY="YOUR-SECRET-KEY-HERE" `
  ALLOWED_HOSTS="localhost,127.0.0.1,*.elasticbeanstalk.com" `
  DB_ENGINE=django.db.backends.postgresql `
  DB_NAME=nomz_db `
  DB_USER=postgres `
  DB_PASSWORD=YOUR-RDS-PASSWORD `
  DB_HOST=nomz-db.ccjqws26yqzi.us-east-1.rds.amazonaws.com `
  DB_PORT=5432 `
  USE_S3=True `
  AWS_ACCESS_KEY_ID=YOUR-AWS-ACCESS-KEY `
  AWS_SECRET_ACCESS_KEY=YOUR-AWS-SECRET-KEY `
  AWS_STORAGE_BUCKET_NAME=nomz-static-files `
  AWS_S3_REGION_NAME=us-east-1 `
  AWS_S3_CUSTOM_DOMAIN=nomz-static-files.s3.us-east-1.amazonaws.com `
  CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://localhost,https://*.elasticbeanstalk.com"
```

**Replace values with YOUR actual values from `.env`**

### Step 2: Verify Variables Are Set

```powershell
eb printenv
```

You should see all your variables listed.

---

## Part G: Deploy Your Application

### Step 1: Initial Deployment

```powershell
eb deploy
```

This will:
- Package your application
- Upload to S3
- Deploy to Elastic Beanstalk instances
- Run migrations
- Collect static files

**Takes 5-10 minutes.**

Monitor progress:
```
Creating new versions...
Uploading to S3...
Starting deployment...
  ...
  Successfully deployed.
```

### Step 2: Check Deployment Status

```powershell
eb status
```

Expected output:
```
Status: Ready
Health: Green
```

### Step 3: View Application Logs

```powershell
eb logs
```

This shows last 100 lines of logs. Check for any errors.

### Step 4: Open Application in Browser

```powershell
eb open
```

This opens your deployed app in default browser at:
```
nomz-prod.us-east-1.elasticbeanstalk.com
```

---

## Part H: Run Django Migrations

### Step 1: SSH into EC2 Instance

```powershell
eb ssh
```

This connects you to the running instance.

### Step 2: Run Migrations

```bash
python manage.py migrate
```

Wait for migrations to complete.

### Step 3: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create admin user.

### Step 4: Exit SSH

```bash
exit
```

---

## Part I: Collect Static Files

Static files should collect automatically from `.ebextensions/django.config`, but verify:

```powershell
eb ssh
python manage.py collectstatic --noinput
exit
```

---

## Part J: Set Up GitHub Actions for Auto-Deployment

### Step 1: Add GitHub Secrets

On GitHub, go to:
```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `AWS_ACCESS_KEY_ID` | Your root AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | Your root AWS secret access key |

### Step 2: Update GitHub Actions Workflow

The `.github/workflows/deploy.yml` file is already created. Just verify it:

```powershell
cat .github\workflows\deploy.yml
```

Should look like:

```yaml
name: Deploy to AWS Elastic Beanstalk

on:
  push:
    branches:
      - production

env:
  EB_ENVIRONMENT_NAME: nomz-prod
  EB_APPLICATION_NAME: nomz-production
  REGION: us-east-1

jobs:
  deploy:
    ...
```

### Step 3: Test Auto-Deployment

Make a small change to your code:

```powershell
# Make a change (e.g., edit a file)
git add .
git commit -m "Test auto-deployment"
git push origin production
```

Go to GitHub → Actions tab and watch the workflow run.

If successful, your app redeploys automatically!

---

## Verification Checklist

After deployment completes:

- [ ] EB status shows "Ready" and "Green"
- [ ] App loads at `nomz-prod.us-east-1.elasticbeanstalk.com`
- [ ] Database connected (check admin panel)
- [ ] S3 static files loading (CSS, JS visible)
- [ ] No errors in `eb logs`
- [ ] Migrations ran successfully

---

## Common Issues & Troubleshooting

### Issue: "InvalidParameterCombination" Error

**Problem:** Environment creation fails

**Solution:**
```powershell
# Delete failed environment
eb terminate nomz-prod

# Try again
eb create nomz-prod --instance-type t3.micro
```

### Issue: "502 Bad Gateway" Error

**Problem:** Application crashes

**Solution:**
```powershell
# Check logs
eb logs

# Likely causes:
# - Database not accessible (check RDS security group)
# - Missing environment variables
# - Python dependency missing
```

### Issue: Database Connection Refused

**Problem:** Cannot connect to RDS

**Solution:**
1. Verify RDS is "Available" in AWS console
2. Check RDS security group allows port 5432 from EB instances
3. Verify DB_HOST, DB_USER, DB_PASSWORD are correct
4. Run: `eb setenv` again to update variables

### Issue: Static Files Not Loading

**Problem:** CSS/JS return 404

**Solution:**
```powershell
# Collect static files
eb ssh
python manage.py collectstatic --noinput
exit

# Redeploy
eb deploy
```

### Issue: GitHub Actions Deployment Fails

**Problem:** Workflow shows red X

**Solution:**
1. Check GitHub Actions logs (Actions tab)
2. Verify AWS credentials in GitHub Secrets
3. Check if EB CLI is installed: `eb --version`
4. Try manual deploy first: `eb deploy`

---

## Useful Commands Reference

```powershell
# View app status
eb status

# View environment variables
eb printenv

# Update environment variables
eb setenv VAR_NAME=value

# Deploy code
eb deploy

# View logs
eb logs --all

# SSH into instance
eb ssh

# Open in browser
eb open

# Terminate environment (WARNING: Deletes everything)
eb terminate nomz-prod

# Help
eb help
```

---

## Next Steps After Deployment

### Add Custom Domain (Optional)

If you bought a domain:
1. Go to AWS Route 53
2. Create hosted zone for your domain
3. Update nameservers at registrar
4. Point to EB load balancer

### Enable HTTPS/SSL (Recommended)

1. Go to AWS Certificate Manager
2. Request certificate for your domain
3. Add to EB load balancer in AWS console

### Monitor Your Application

1. AWS CloudWatch → Metrics
2. Monitor CPU, memory, requests
3. Set up alarms for issues

### Scale Your Application

If traffic increases:
```powershell
eb scale 2
```

This adds more EC2 instances.

---

## Security Checklist

- ✅ `.env` file NOT committed to Git (verify `.gitignore`)
- ✅ AWS credentials stored in GitHub Secrets (NOT in code)
- ✅ RDS password is strong
- ✅ S3 bucket access limited to your app
- ✅ EB instance type is minimal (t3.micro for cost)
- ✅ Database backups enabled
- ✅ HTTPS/SSL enabled on custom domain

---

## Cost Estimation (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| Elastic Beanstalk | t3.micro | ~$10-15 |
| RDS PostgreSQL | db.t3.micro | ~$10-15 |
| S3 Storage | First 1GB | Free to ~$1 |
| Data Transfer | Varies | $0-5 |
| **TOTAL** | **Free tier eligible** | **~$20-30** |

(Cheaper if you use AWS free tier first 12 months)

---

## Success!

Your Django application is now deployed to AWS Elastic Beanstalk! 🎉

**Your app is live at:**
```
nomz-prod.us-east-1.elasticbeanstalk.com
```

**Auto-deployment configured:**
- Push to `production` branch → GitHub Actions runs → Auto-deploys to EB

---

**Need help? Check:**
- AWS EB Documentation: https://docs.aws.amazon.com/elasticbeanstalk/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- EB CLI Guide: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
