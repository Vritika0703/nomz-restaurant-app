# Phase 1: Detailed AWS Resource Setup Guide

This guide walks you through creating all necessary AWS resources for your Django application deployment.

---

## Prerequisites

- AWS Account with billing enabled
- AWS Management Console access
- Text editor to save credentials and endpoints

> ⚠️ **IMPORTANT**: Save all credentials and endpoints in a secure location. You'll need them for deployment.

---

## Part 1: Create RDS PostgreSQL Database

### Step 1.1: Navigate to RDS Console

1. Go to **AWS Management Console** (https://console.aws.amazon.com)
2. Search for **RDS** in the search bar at the top
3. Click **RDS** to open the RDS Dashboard
4. You should see the RDS welcome page with options

   ![Expected: RDS Dashboard with "Create database" button]

### Step 1.2: Start Database Creation

1. Click **"Create database"** button (orange button on the dashboard)
2. You'll be taken to the database creation wizard

   ```
   CREATE DATABASE PAGE - Step 1: Choose Database Engine
   ```

### Step 1.3: Select PostgreSQL Engine

In the **"Choose a database engine"** section:

1. Look for **PostgreSQL** in the list
2. Click on **PostgreSQL** (or the radio button next to it)

   ```
   Available options:
   - Amazon Aurora (MySQL-compatible)
   - Amazon Aurora (PostgreSQL-compatible)
   - MySQL
   - MariaDB
   - PostgreSQL  ← SELECT THIS
   - Oracle Database
   - SQL Server
   ```

3. After selecting PostgreSQL, look for **Edition** options below
4. Make sure **PostgreSQL** (standard PostgreSQL) is selected, NOT "Aurora PostgreSQL"

### Step 1.4: Configure Database Details

After selecting PostgreSQL, scroll down to the **"Templates"** section:

1. **Templates**: Select **"Free tier"** (if eligible - gives you a free tier instance)
   - This qualifies for AWS free usage tier
   - Sufficient for testing and small production workloads
   - Alternative: Select "Production" for more robust setup

   ```
   Template Options:
   ☐ Production
   ☐ Dev/Test
   ☑ Free tier  ← SELECT THIS (if available)
   ```

### Step 1.5: Set Database Identity

Find the **"DB instance identifier"** section:

1. In the field **"DB instance identifier"**, enter:
   ```
   nomz-db
   ```

2. Scroll down to **"Credentials Settings"**:

   - **Master username**: `postgres` (default, keep it)
   
   - **Master password**: 
     - Click **"Generate password"** button (recommended)
     - OR manually enter a strong password
     - **SAVE THIS PASSWORD** - you'll need it for deployment!
     - Example strong password format: `Nomz@Prod2024!Secure`
     
   - **Confirm password**: Re-enter the same password

   ```
   Credentials Settings:
   ├─ Master username: postgres
   ├─ Master password: ••••••••••••••
   └─ Confirm password: ••••••••••••••
   ```

### Step 1.6: Configure Storage Settings

Scroll down to **"Storage"** section:

1. **Storage type**: Select **"General Purpose (SSD)"** (default)
2. **Allocated storage**: Set to **`20 GB`** (minimum for free tier)
   - Slider or number field to adjust

   ```
   Storage Configuration:
   ├─ Storage type: General Purpose (SSD) (gp3)
   ├─ Allocated storage: 20 GB
   └─ Storage autoscaling: ☑ (optional, keep enabled)
   ```

### Step 1.7: Configure Connectivity

Scroll down to **"Connectivity"** section - THIS IS IMPORTANT:

1. **Virtual Private Cloud (VPC)**: Keep default (select your VPC)
   
2. **DB Subnet Group**: Keep default or select existing

3. **Public accessibility**: 
   - **SELECT: "Yes"** 
   - (This allows your Elastic Beanstalk to connect to the database)
   - ⚠️ Don't worry about security - we'll configure security groups to restrict access

4. **VPC Security Group**: 
   - Select **"Create new"** (recommended)
   - Name the security group: `nomz-rds-sg`
   - This creates a firewall for the database

5. **Database port**: Keep as **`5432`** (standard PostgreSQL port)

   ```
   Connectivity Configuration:
   ├─ VPC: default
   ├─ Public accessibility: ⊙ Yes  ← SELECT THIS
   ├─ VPC Security Group: Create new
   │   └─ Name: nomz-rds-sg
   └─ Database port: 5432
   ```

### Step 1.8: Configure Initial Database Name

Scroll down to **"Database options"** section:

1. Find **"Initial database name"** field
2. Enter: `nomz_db`
   
   ```
   Database Options:
   ├─ Initial database name: nomz_db
   ├─ DB parameter group: default.postgres14  (or your version)
   ├─ DB option group: default
   └─ Backup retention period: 7 days
   ```

3. **Backups**: Keep default (7 days backup retention)

4. **Encryption**: Keep default (enabled) - recommend for production

### Step 1.9: Additional Settings (Optional but Recommended)

Scroll down further if needed:

1. **Backup retention period**: Keep as **`7 days`** (minimum recommended)
2. **Backup window**: Keep as **"No preference"** (AWS default)
3. **Enable deletion protection**: 
   - Consider checking this to prevent accidental deletion
   - Optional: You can enable this after confirming the database works

### Step 1.10: Review and Create

1. Scroll to bottom of the page
2. Review all settings:
   - DB Instance Identifier: `nomz-db` ✓
   - Engine: PostgreSQL ✓
   - Master username: `postgres` ✓
   - Database name: `nomz_db` ✓
   - Public accessibility: Yes ✓

3. Click **"Create database"** button (orange button at bottom)

   ```
   ✓ All settings configured
   → Click: [Create database]
   ```

### Step 1.11: Database Creation In Progress

1. You'll see a notification: **"Creating database nomz-db"**
2. The page shows the database with status **"Creating"**
3. **This takes 5-15 minutes** - be patient!

   Monitor progress:
   - Status shows: "Creating" → "Backing up" → "Available"
   - Look for the **blue circle icon** with "Creating" text

   ```
   Database: nomz-db
   Status: Creating (●)
   Time elapsed: ~2 minutes...
   ```

### Step 1.12: Database Ready - Save Endpoint Information

Once status changes to **"Available"** (green circle):

1. Click on **"nomz-db"** in the database list to open its details page
2. Scroll down to **"Connectivity & security"** section
3. **SAVE these values:**

   ```
   📝 SAVE THESE VALUES:
   
   ✓ Endpoint: nomz-db.c12k9jd4k2.us-east-1.rds.amazonaws.com
     (Format: xxx.xxxxx.region.rds.amazonaws.com)
   
   ✓ Port: 5432
   
   ✓ Database name: nomz_db
   
   ✓ Master username: postgres
   
   ✓ Master password: [Password you created above]
   ```

4. Keep these in a secure location (password manager recommended)

---

## Part 2: Create S3 Bucket for Static Files

### Step 2.1: Navigate to S3 Console

1. Go back to **AWS Management Console**
2. Search for **"S3"** in the search bar
3. Click **"S3"** to open the S3 Dashboard
4. Click **"Buckets"** in the left menu (if not already selected)

   ```
   S3 Dashboard
   ├─ Buckets (← click here)
   └─ Block Public Access settings for this account
   ```

### Step 2.2: Create New Bucket

1. Click **"Create bucket"** button (orange button at top right)
2. You'll see the bucket creation form

### Step 2.3: Name Your Bucket

In the **"Bucket name"** field:

1. Enter: `nomz-static-files`
   
   > ⚠️ **IMPORTANT**: S3 bucket names must be:
   > - Globally unique (across ALL AWS accounts worldwide)
   > - If name exists, add your student ID or date: `nomz-static-files-2024`
   > - Lowercase only
   > - No underscores, only hyphens

2. If you get an error saying name is taken, try:
   - `nomz-static-files-2024`
   - `nomz-files-prod`
   - `nomz-static-<yourname>`

   ```
   Bucket name: nomz-static-files
   (If unavailable: nomz-static-files-2024)
   ```

### Step 2.4: Select Region

Find the **"AWS Region"** option:

1. Click the dropdown menu
2. Select the region **closest to you OR same as your RDS database**
   - Example: `us-east-1` (N. Virginia)
   - Common US region: `us-west-2` (Oregon)
   - Check which you used for RDS

   ```
   AWS Region: us-east-1 (N. Virginia)
   OR: us-west-2 (Oregon)
   
   Choose same region as your RDS database!
   ```

### Step 2.5: Configure Public Access Settings

Find **"Block Public Access settings for this bucket"**:

1. Click to expand this section
2. You'll see 4 checkboxes:

   ```
   ☑ Block all public access (UNCHECK THIS)
   ├─ ☑ Block public access to ACLs (UNCHECK)
   ├─ ☑ Block public access to bucket policies (UNCHECK)
   ├─ ☑ Block public ACLs (UNCHECK)
   └─ ☑ Block bucket policies (UNCHECK)
   ```

3. **UNCHECK all four boxes** so the bucket can be public
   - Public = accessible for static file serving
   - Recommended: Know what you're making public (just static files)

   ```
   ☐ Block all public access (UNCHECKED)
   ├─ ☐ Block public access to ACLs (UNCHECKED)
   ├─ ☐ Block public access to bucket policies (UNCHECKED)  
   ├─ ☐ Block public ACLs (UNCHECKED)
   └─ ☐ Block bucket policies (UNCHECKED)
   ```

### Step 2.6: Other Settings (Keep Defaults)

You can keep all other settings as default:

```
✓ Versioning: Disabled (recommended)
✓ Server-side encryption: Disabled (for now)
✓ Object Lock: Disabled
```

### Step 2.7: Create Bucket

1. Scroll to the bottom
2. Click **"Create bucket"** button
3. You'll see: **"Successfully created bucket nomz-static-files"**

   ```
   ✓ Bucket created successfully
   ```

### Step 2.8: Add Public Read Policy to Bucket

Now we need to make files in this bucket publicly readable:

1. Click on your bucket name **"nomz-static-files"** in the list
2. You're now inside the bucket (empty)
3. Click the **"Permissions"** tab at the top

   ```
   Bucket: nomz-static-files
   ├─ Objects (empty)
   ├─ Properties
   └─ Permissions (← click here)
   ```

### Step 2.9: Edit Bucket Policy

In the **"Permissions"** tab:

1. Scroll down to **"Bucket policy"** section
2. Click **"Edit"** button
3. You'll see an empty policy editor

   ```
   Bucket policy section:
   [Policy text area - empty or with existing policy]
   [Edit] [Cancel]
   ```

### Step 2.10: Add Public Read Policy

In the **bucket policy editor**, paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nomz-static-files/*"
        }
    ]
}
```

**IMPORTANT**: Replace `nomz-static-files` with your actual bucket name if different!

```json
Example if bucket is "nomz-static-files-2024":

"Resource": "arn:aws:s3:::nomz-static-files-2024/*"
```

### Step 2.11: Save Bucket Policy

1. Click **"Save"** button
2. You'll see: **"Changes have been saved"**
3. You might see a warning about "public bucket" - this is expected and fine

   ```
   ✓ Policy saved
   ⚠️ Warning: This bucket has a public bucket policy (OK for static files)
   ```

### Step 2.12: Save Bucket Information

**SAVE these values:**

```
📝 SAVE BUCKET INFORMATION:

✓ Bucket name: nomz-static-files
  (or whatever you named it if different)

✓ AWS Region: us-east-1
  (or your selected region)

✓ Bucket ARN: arn:aws:s3:::nomz-static-files
  (usually shown in bucket properties)
```

---

## Part 3: Create IAM User for Application Access

### Step 3.1: Navigate to IAM Console

1. Go back to **AWS Management Console**
2. Search for **"IAM"** in the search bar
3. Click **"IAM"** to open the IAM Dashboard

   ```
   IAM Dashboard
   ```

### Step 3.2: Access Users Section

In the left sidebar menu:

1. Click **"Users"** (not "User groups")

   ```
   Left Menu:
   ├─ Dashboard
   ├─ Users (← click here)
   ├─ User groups
   ├─ Roles
   ├─ Policies
   └─ ...
   ```

2. You'll see the Users page (might be empty)

### Step 3.3: Create New User

1. Click **"Create user"** button (top right)
2. You'll see the Create User form

   ```
   Create user page
   ```

### Step 3.4: Configure User Details

In the **User details** section:

1. **User name**: Enter `nomz-app`
   
   ```
   User name: nomz-app
   ```

2. Click **"Next"** button to continue

### Step 3.5: Set Permissions

You're now at the **"Set permissions"** step:

1. Look for permission options:
   - "Add user to group"
   - "Attach policies directly"  ← **SELECT THIS**
   - "Copy permissions from existing user"

2. Select **"Attach policies directly"**

   ```
   Select permission method:
   ○ Add user to group
   ⊙ Attach policies directly  ← SELECT THIS
   ○ Copy permissions from existing user
   ```

### Step 3.6: Attach S3 Policy

You should now see a "Permissions policies" search box:

1. In the **search box**, type: `S3`
2. You'll see suggested policies appear
3. Look for **"AmazonS3FullAccess"**
4. Click the **checkbox** next to **"AmazonS3FullAccess"**

   ```
   Search for policies: S3
   
   Results:
   ☐ AmazonS3FullAccess  ← CHECK THIS ONE
   ☐ AmazonS3OutpostsFullAccess
   ☐ AmazonS3ObjectLambdaFullAccess
   ☐ ...
   ```

5. The checkbox next to "AmazonS3FullAccess" should now be **checked** ✓

   ```
   ✓ Selected policies:
   └─ ✓ AmazonS3FullAccess
   ```

### Step 3.7: Review and Create User

1. Click **"Next"** button to review
2. Review page shows:
   - User name: `nomz-app` ✓
   - Policies: `AmazonS3FullAccess` ✓

3. Click **"Create user"** button

   ```
   ✓ User creation successful
   ```

### Step 3.8: Generate Access Keys

After user is created, you should see a success message. Now you need to create access keys:

1. Find the newly created user **"nomz-app"** in the users list
2. Click on **"nomz-app"** to open the user details page

   ```
   IAM Users:
   ├─ nomz-app (← click here)
   └─ ...
   ```

### Step 3.9: Create Access Key

On the **nomz-app user details** page:

1. Find the **"Access keys"** section (scroll down if needed)
2. Click **"Create access key"** button

   ```
   Access keys section:
   [Create access key] button
   
   (Might show "No access keys")
   ```

3. You'll see a dialog asking what the access key is for
4. Select **"Command Line Interface (CLI)"**

   ```
   What's your use case?
   ○ AWS Management Console access (web login)
   ○ Application running outside AWS
   ⊙ Command Line Interface (CLI)  ← SELECT THIS
   ☐ I understand the above recommendation (check this)
   ```

5. Check the box: **"I understand the above recommendation"**
6. Click **"Create access key"**

### Step 3.10: Save Access Key Information

⚠️ **CRITICAL**: This is the only time you'll see these! Save them immediately!

You'll see a page showing:

```
Access key created successfully!

Access key ID:        AKIA1234567890ABCDEF
Secret access key:    wJalrXUtnFEMI/K7MDENG+39qZr47C91234567890
```

**IMMEDIATELY SAVE THESE** in a secure location:

```
📝 SAVE ACCESS KEY INFORMATION:

✓ Access key ID: AKIA1234567890ABCDEF

✓ Secret access key: wJalrXUtnFEMI/K7MDENG+39qZr47C91234567890

⚠️ SAVE TO:
  - Password manager (1Password, Bitwarden, etc.)
  - Secure note
  - DO NOT commit to GitHub
  - DO NOT share publicly
```

### Step 3.11: Download Credentials File (Optional but Recommended)

On the same page, you'll see an option to **"Download .csv file"**:

1. Click **"Download .csv file"** button
2. This downloads a file with your credentials
3. Store this file securely (encrypted storage)

   ```
   [Download .csv file] button
   
   File contains:
   - Access key ID
   - Secret access key
   - Console login link
   ```

---

## Summary: Information to Save

You now have all AWS resources created. **SAVE THIS INFORMATION SECURELY:**

### RDS Database Information

```
DB Engine:        PostgreSQL
DB Instance:      nomz-db
Endpoint:         nomz-db.c12k9jd4k2.us-east-1.rds.amazonaws.com
Port:             5432
Database Name:    nomz_db
Master User:      postgres
Master Password:  [Your secure password]

SAVED? _____ (checkmark when saved)
```

### S3 Bucket Information

```
Bucket Name:      nomz-static-files
Region:           us-east-1
Bucket ARN:       arn:aws:s3:::nomz-static-files

SAVED? _____ (checkmark when saved)
```

### IAM User Information

```
Username:         nomz-app
Access Key ID:    AKIA1234567890ABCDEF
Secret Key:       wJalrXUtnFEMI/K7MDENG+39qZr47C91234567890
Permissions:      AmazonS3FullAccess

SAVED? _____ (checkmark when saved)
```

---

## Next Steps: Configure Environment Variables

Once you have all this information, update your `.env` file:

```bash
# Database Configuration (AWS RDS PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nomz_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=nomz-db.c12k9jd4k2.us-east-1.rds.amazonaws.com
DB_PORT=5432

# AWS S3 for Static & Media Files
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG+39qZr47C91234567890
AWS_STORAGE_BUCKET_NAME=nomz-static-files
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=nomz-static-files.s3.us-east-1.amazonaws.com
```

---

## Troubleshooting

### Cannot create bucket - name already taken?
- Try: `nomz-static-files-yourname`
- Or: `nomz-static-files-2024`
- S3 names are globally unique

### Database still shows "Creating" after 30 minutes?
- Usually takes 5-15 minutes
- Check RDS console for any errors
- You can check CloudFormation events for details

### Cannot connect to RDS?
- Ensure "Public accessibility" is set to "Yes"
- Check RDS security group allows inbound traffic on port 5432
- Verify credentials are correct

### Access denied when trying to edit S3 bucket policy?
- Verify you're logged in as admin or root user
- Check IAM permissions for your account

---

## Security Best Practices

1. **Rotate credentials regularly** (every 90 days)
2. **Never commit `.env` file to GitHub** (already in `.gitignore`)
3. **Add second factor authentication** to AWS account
4. **Restrict S3 bucket** to only necessary files
5. **Monitor RDS** for unauthorized access
6. **Use VPC security groups** to restrict database access

---

**You're now ready to proceed to Phase 2: Elastic Beanstalk Deployment!**
