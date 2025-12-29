# 📧 Email Service Setup Guide

## ✅ Email Service is NOW IMPLEMENTED!

All email functionality has been integrated into the application:

### Implemented Features:
1. ✅ **Verification Email** - Sent after user registration
2. ✅ **Password Reset Email** - Sent when user requests password reset
3. ✅ **Magic Link Email** - Sent for passwordless login
4. ✅ **Invoice Email** - Sent after successful payment

---

## 🚀 Quick Setup (SendGrid)

### 1. Create SendGrid Account
1. Go to https://sendgrid.com/
2. Sign up for free account (100 emails/day free)
3. Verify your email address

### 2. Get API Key
1. Go to Settings → API Keys
2. Click "Create API Key"
3. Name: `AutoFlow Backend`
4. Permissions: **Full Access** (or at least Mail Send)
5. Copy the API key (you won't see it again!)

### 3. Verify Sender Identity
1. Go to Settings → Sender Authentication
2. Choose "Single Sender Verification" (easiest for testing)
3. Fill in your details:
   - From Name: `AutoFlow`
   - From Email: `noreply@yourdomain.com` (or your email for testing)
4. Verify the email address

### 4. Configure Environment Variables

Add to your `.env` file:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com  # Must match verified sender
SENDGRID_FROM_NAME=AutoFlow

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000  # Change to your frontend URL
```

### 5. Test Email Sending

Run the application and test:

```bash
# 1. Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Check your email for verification link!

# 2. Request password reset
curl -X POST http://localhost:8000/api/v1/auth/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# Check your email for reset link!

# 3. Request magic link
curl -X POST http://localhost:8000/api/v1/auth/magic-link/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# Check your email for login link!
```

---

## 🔧 Alternative: AWS SES

If you prefer AWS SES instead of SendGrid:

### 1. Install boto3
```bash
pip install boto3
```

### 2. Update email_service.py

Replace SendGrid client with boto3 SES client:

```python
import boto3
from botocore.exceptions import ClientError

class EmailService:
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            region_name='us-east-1',  # Your AWS region
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.from_email = settings.SENDGRID_FROM_EMAIL  # Reuse same config
        
    async def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None):
        try:
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Html': {'Data': html_content},
                        'Text': {'Data': plain_content or ''}
                    }
                }
            )
            return True
        except ClientError as e:
            logger.error(f"Error sending email: {e}")
            return False
```

### 3. Configure AWS Credentials

Add to `.env`:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

---

## 📊 Email Templates

All email templates are defined in `app/services/email_service.py`:

- **Verification Email**: Lines 74-118
- **Password Reset Email**: Lines 120-166
- **Magic Link Email**: Lines 168-216
- **Invoice Email**: Lines 218-266

### Customizing Templates

Edit the HTML/plain text in `email_service.py`:

```python
async def send_verification_email(self, to_email: str, verification_token: str, frontend_url: str):
    verification_link = f"{frontend_url}/auth/verify-email?token={verification_token}"
    
    subject = "Verify your email address"  # ← Customize
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <!-- Your custom HTML here -->
            <h2>Welcome to AutoFlow!</h2>
            <a href="{verification_link}">Verify Email</a>
        </body>
    </html>
    """
    # ...
```

---

## 🧪 Testing Without Real Emails

For development/testing without sending real emails:

### Option 1: Mock Email Service

Create `app/services/mock_email_service.py`:

```python
class MockEmailService:
    async def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None):
        print(f"\n📧 MOCK EMAIL")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Content: {html_content[:100]}...")
        return True
    
    async def send_verification_email(self, *args, **kwargs):
        return await self.send_email(kwargs['to_email'], "Verification Email", "...")
    
    # ... implement other methods
```

Then in `auth_service.py`:

```python
from app.services.mock_email_service import MockEmailService

class AuthService:
    def __init__(self, db: AsyncSession):
        # ...
        if settings.DEBUG:
            self.email_service = MockEmailService()  # ← Use mock in dev
        else:
            self.email_service = EmailService()
```

### Option 2: MailHog (Email Testing Tool)

1. Install MailHog: https://github.com/mailhog/MailHog
2. Run: `mailhog`
3. Configure SMTP in email_service.py to use localhost:1025
4. View emails at http://localhost:8025

---

## 🔍 Troubleshooting

### Emails not sending?

1. **Check SendGrid API Key**
   ```bash
   # Test API key
   curl -X POST https://api.sendgrid.com/v3/mail/send \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "personalizations": [{"to": [{"email": "test@example.com"}]}],
       "from": {"email": "noreply@yourdomain.com"},
       "subject": "Test",
       "content": [{"type": "text/plain", "value": "Test"}]
     }'
   ```

2. **Check Sender Verification**
   - Go to SendGrid → Settings → Sender Authentication
   - Make sure your `SENDGRID_FROM_EMAIL` is verified

3. **Check Application Logs**
   ```bash
   # Look for email service logs
   tail -f logs/app.log | grep -i email
   ```

4. **Check Environment Variables**
   ```python
   # In Python shell
   from app.core.config import settings
   print(settings.SENDGRID_API_KEY)  # Should not be None
   print(settings.SENDGRID_FROM_EMAIL)
   ```

### Emails going to spam?

1. **Set up SPF/DKIM** (SendGrid does this automatically)
2. **Use verified domain** instead of personal email
3. **Add unsubscribe link** (for production)
4. **Avoid spam trigger words** in subject/content

---

## 📝 Production Checklist

Before deploying to production:

- [ ] Use verified domain email (not gmail/yahoo)
- [ ] Set up SPF/DKIM/DMARC records
- [ ] Use environment-specific `FRONTEND_URL`
- [ ] Add rate limiting to email endpoints
- [ ] Monitor SendGrid usage/quota
- [ ] Set up email bounce/complaint handling
- [ ] Add unsubscribe functionality (if sending marketing emails)
- [ ] Test all email flows in staging environment
- [ ] Set up email logging/monitoring

---

## 🎯 Summary

**Email Service Status: ✅ FULLY IMPLEMENTED**

All 4 email types are now working:
1. ✅ Verification Email
2. ✅ Password Reset Email
3. ✅ Magic Link Email
4. ✅ Invoice Email

**Setup Time: 5-10 minutes** (SendGrid account + API key)

**Cost: FREE** (100 emails/day with SendGrid free tier)

**Next Steps:**
1. Create SendGrid account
2. Get API key
3. Add to `.env` file
4. Test registration flow
5. Done! 🎉
