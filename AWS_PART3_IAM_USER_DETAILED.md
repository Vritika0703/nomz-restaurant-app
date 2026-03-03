# Part 3: Detailed IAM User Creation Guide

Complete step-by-step instructions to create an IAM user for your Django application to access AWS S3.

---

## Overview

An **IAM User** is an AWS identity that allows your application to authenticate and access AWS services (like S3). Instead of using your main AWS account credentials (NEVER do this!), you create a limited-permission user that can only access S3.

**What you'll create:**
- Username: `nomz-app`
- Permissions: S3 Full Access (only for your static files bucket)
- Access Keys: Used by your Django app to upload/serve files

---

## Prerequisites

- AWS Management Console open
- Logged in as your main AWS account (or admin user)

---

## Step-by-Step Guide

### Step 1: Navigate to IAM Console

1. Open **AWS Management Console** (https://console.aws.amazon.com)
2. In the search bar at the top, search for: **`IAM`**

   ```
   Search box: IAM
   ```

3. In the results, click **"IAM"** (the Identity and Access Management service)

   ```
   Search Results:
   ├─ IAM - Identity and Access Management ← CLICK THIS
   ├─ Lambda
   ├─ RDS
   └─ ...
   ```

4. You'll be taken to the IAM Dashboard

   ```
   IAM Dashboard
   ├─ Summary
   ├─ Users
   ├─ Access Management
   └─ Security Tools
   ```

---

### Step 2: Access the Users Section

In the **left sidebar** of the IAM Console, find the menu:

```
Left Sidebar Menu:
├─ Dashboard
├─ User groups
├─ Users              ← CLICK HERE
├─ Roles
├─ Policies
├─ Identity providers
├─ Account settings
└─ ...
```

1. Click on **"Users"** (not "User groups")

2. You'll see the **"Users"** page

   ```
   Users page
   ├─ Create user  [Button at top right]
   ├─ [List of existing users - might be empty]
   └─ ...
   ```

---

### Step 3: Start Creating a New User

1. Look for the **"Create user"** button at the top right of the page
2. Click **"Create user"** button (orange/blue button)

   ```
   [Create user] ← CLICK THIS BUTTON
   ```

3. You'll see the **"Create user"** form/wizard

   ```
   Specify user details
   ├─ User name field
   ├─ Provide user console access (optional)
   └─ [Next] button
   ```

---

### Step 4: Enter the Username

In the **"Specify user details"** section:

1. Find the **"User name"** field (text input box)
2. Click on the field and enter: **`nomz-app`**

   ```
   User name: |nomz-app________________|
   ```

3. **Skip** the console access options (leave unchecked):
   - Do NOT check "Provide user console access"
   - This user only needs programmatic access (API keys)

   ```
   ☐ Provide user console access (leave UNCHECKED)
     └─ This would create a web login (we don't need this)
   ```

4. Once username is entered, click **"Next"** button at the bottom

   ```
   User name: nomz-app ✓
   Console access: ☐ (unchecked)
   
   [Previous] [Next] ← CLICK "Next"
   ```

---

### Step 5: Set Permissions

You're now at the **"Set permissions"** step. This is where you define what this user can do.

```
Set permissions page
├─ Permission options
└─ [Next] button
```

**You'll see three permission options:**

```
Permission options:
○ Add user to group
○ Attach policies directly          ← SELECT THIS ONE
○ Copy permissions from existing user
```

1. Click the radio button next to **"Attach policies directly"**

   ```
   ⊙ Attach policies directly  ← SELECT THIS
   ```

   This lets you attach specific AWS permission policies to the user.

---

### Step 6: Search for S3 Policy

After selecting "Attach policies directly", you should see a **search box** for policies.

```
Permissions policies section:
[Search for policies: |_______________|]

Search results:
├─ [List will populate as you type]
└─ ...
```

1. Click in the **search box**
2. Type: **`S3`**

   ```
   Search: |S3______________|
   ```

3. Press **Enter** or wait for results to appear

4. You should see several S3-related policies in the results:

   ```
   Search Results:
   ☐ AmazonS3FullAccess            ← SELECT THIS ONE
   ☐ AmazonS3ObjectLambdaFullAccess
   ☐ AmazonS3OutpostsFullAccess
   ☐ AmazonS3ReadOnlyAccess
   ☐ ...
   ```

---

### Step 7: Attach S3 Full Access Policy

1. Find **"AmazonS3FullAccess"** in the search results
2. Click the **checkbox** next to it to select it

   ```
   ☑ AmazonS3FullAccess  ← CHECK THIS
   ```

3. After checking, you should see it appear in a **"Selected policies"** section:

   ```
   Selected policies:
   ├─ ✓ AmazonS3FullAccess
   └─ ...
   ```

   The checkbox should show as **checked** ✓

4. Scroll down and look for the **"Next"** button
5. Click **"Next"** to continue

   ```
   Selected policies: AmazonS3FullAccess ✓
   
   [Previous] [Next] ← CLICK "Next"
   ```

---

### Step 8: Review User Configuration

You're now at the **"Review and create"** section. This shows a summary of everything:

```
Review page:
├─ User name: nomz-app
├─ Permissions: AmazonS3FullAccess
└─ [Create user] button
```

**Verify:**
- ✓ User name: `nomz-app` 
- ✓ Permissions: `AmazonS3FullAccess`
- ✓ Console access: NOT enabled

If everything looks correct, click **"Create user"** button at the bottom

```
User Details:
├─ Username: nomz-app ✓
├─ Permissions: AmazonS3FullAccess ✓
├─ Console sign-in: Disabled ✓

[Back] [Create user] ← CLICK "Create user"
```

---

### Step 9: User Created Successfully

After clicking "Create user", you should see:

```
✓ User nomz-app has been created successfully
```

You'll see a page showing:
- User name: `nomz-app`
- Success message
- Next steps

---

### Step 10: Find Your User in the Users List

1. You should be taken back to the **Users** page
2. Look for **"nomz-app"** in the users list
3. Click on **"nomz-app"** to open the user details page

   ```
   Users:
   ├─ nomz-app  ← CLICK HERE
   └─ ...
   ```

---

### Step 11: Navigate to Access Keys Section

On the **nomz-app user details** page:

1. Look for the **"Security credentials"** tab at the top

   ```
   Tabs:
   ├─ Summary (might be selected)
   ├─ Permissions
   ├─ Security credentials  ← CLICK THIS TAB
   ├─ Access Analyzer
   └─ ...
   ```

2. Click on **"Security credentials"** tab

3. You should see several sections on this page:
   - Password
   - **Access keys** ← This is what we need
   - Temporary security credentials
   - SSH public keys

---

### Step 12: Create Access Key

In the **"Access keys"** section:

1. You should see: **"No access keys"** (or a button to create one)
2. Click **"Create access key"** button

   ```
   Access keys section:
   [Create access key] button  ← CLICK THIS
   ```

3. A dialog box will appear asking **"What's your use case?"**

   ```
   Dialog: Select use case
   ├─ ○ AWS Management Console access
   ├─ ○ Application running outside AWS
   ├─ ⊙ Command Line Interface (CLI)     ← SELECT THIS
   ├─ (other options)
   └─ [Next] button
   ```

4. **Select: "Command Line Interface (CLI)"** (should be the third option)

   ```
   ⊙ Command Line Interface (CLI)  ← SELECT THIS
   ```

5. You'll see a checkbox that says:
   ```
   ☐ I understand the recommendations above (check if appropriate)
   ```

6. Check this checkbox to confirm you understand

   ```
   ☑ I understand the recommendations above
   ```

7. Click **"Create access key"** button to proceed

---

### Step 13: Save Your Access Keys (CRITICAL!)

⚠️ **THIS IS THE MOST IMPORTANT STEP** ⚠️

You'll now see a page with your credentials. **THIS IS THE ONLY TIME YOU'LL SEE THESE!**

```
Access key created successfully!

Access key ID:     AKIA7EXAMPLE1234567
Secret access key: wJalrXUtnFEMI/K7MDENG/39qZZzZExample1234
```

**YOU MUST SAVE THESE IMMEDIATELY!**

Create a secure document with this information:

```
📝 SAVE THIS SECURELY:

Access key ID:
AKIA7EXAMPLE1234567

Secret access key:
wJalrXUtnFEMI/K7MDENG/39qZZzZExample1234

Region: us-east-1
User: nomz-app

⚠️ WARNING: 
- DO NOT share these with anyone
- DO NOT commit to GitHub
- DO NOT post on forums or Stack Overflow
- Store in password manager (LastPass, 1Password, Bitwarden)
- Treat like passwords
```

---

### Step 14: Download Credentials CSV (Recommended)

On the same page, you should see a button:

```
[Download .csv file] button
```

1. Click **"Download .csv file"**
2. This downloads a file named: `nomz-app_accessKeys.csv`
3. This file contains:
   - Access key ID
   - Secret access key
   - Console login URL

4. **Store this file securely**:
   - Don't commit to Git
   - Don't share
   - Use encrypted storage

   ```
   Downloaded file: nomz-app_accessKeys.csv
   
   Contents:
   User name,Access key ID,Secret access key
   nomz-app,AKIA7EXAMPLE1234567,wJalrXUtnFEMI/K7MDENG/39qZZzZ...
   ```

---

### Step 15: Verify Keys Are Created

1. On the same page, click **"Done"** button (if available)
2. Go back to the **nomz-app user page**
3. Click **"Security credentials"** tab again
4. In the **"Access keys"** section, you should now see:

   ```
   Access key ID: AKIA7EXAMPLE1234567
   Status: Active
   Created: [Today's date]
   Last used: Never
   ```

   This confirms your access key was successfully created.

---

## Information to Save

You now have everything for Phase 1! Keep this information secure:

### **Complete IAM User Information**

```
📋 SAVE THIS INFORMATION:

Username:          nomz-app
Permission Level:  AmazonS3FullAccess

Access key ID:     AKIA7EXAMPLE1234567
Secret access key: wJalrXUtnFEMI/K7MDENG/39qZZzZExample1234

Status:            ✓ Active
Created:           [Date]

SAVED LOCATION:    ________________
  (password manager, encrypted file, etc.)

SECURELY ENCRYPTED?: ☐ Yes ☐ No
```

---

## Next Steps

### Use These Credentials In Your `.env` File

Update your `.env` file with these values:

```env
# AWS S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA7EXAMPLE1234567
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/39qZZzZExample1234
AWS_STORAGE_BUCKET_NAME=nomz-static-files
AWS_S3_REGION_NAME=us-east-1
```

### Verify in AWS Console

Later, you can verify access works by:
1. Going back to IAM → Users → nomz-app
2. Checking "Last used" timestamp updates when your app accesses S3

---

## Troubleshooting

### Can't find "AmazonS3FullAccess" policy?

1. Clear the search box
2. Type just `S3` (shorter search)
3. Or use: `AmazonS3` (partial match)
4. Look for policies starting with "Amazon"

### Access Key not appearing after creation?

1. Refresh the page (F5)
2. Go: Users → nomz-app → Security credentials
3. Scroll to "Access keys" section
4. Keys should be listed there

### Lost my Secret Access Key?

⚠️ **You cannot retrieve a lost secret key!**

You must create a new one:
1. Go to nomz-app → Security credentials
2. Find the old access key
3. Click "Delete" or "Deactivate"
4. Create a new access key
5. Save the new secret key immediately

### Want to Delete/Deactivate Keys?

If you ever need to revoke access:
1. Users → nomz-app → Security credentials
2. Find the access key
3. Click **"Deactivate"** (temporary) or **"Delete"** (permanent)
4. This stops the application from accessing S3

---

## Security Best Practices

✓ Use strong, unique access keys
✓ Rotate credentials every 90 days
✓ Never commit credentials to Git
✓ Use AWS Secrets Manager for production
✓ Monitor "Last used" date in IAM console
✓ Delete unused access keys
✓ Review IAM user list regularly

---

## Summary

**You've successfully:**
1. ✓ Created IAM user: `nomz-app`
2. ✓ Attached S3 permissions
3. ✓ Generated access keys
4. ✓ Downloaded credentials file
5. ✓ Saved keys securely

**You now have all three Phase 1 components ready:**
- ✓ RDS PostgreSQL Database
- ✓ S3 Bucket for static files
- ✓ IAM User with credentials

**Next:** Use these credentials to configure your `.env` file and deploy to Elastic Beanstalk (Phase 2)!
