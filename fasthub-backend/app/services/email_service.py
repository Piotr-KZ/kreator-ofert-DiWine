"""
Email service
SendGrid integration for sending emails
"""

import logging
from typing import Any, Dict, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid"""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME

        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
            logger.warning("SendGrid API key not configured - emails will not be sent")

    async def send_email(
        self, to_email: str, subject: str, html_content: str, plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            plain_content: Plain text email content (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.warning(f"Email not sent (SendGrid not configured): {subject} to {to_email}")
            return False

        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            if plain_content:
                message.plain_text_content = Content("text/plain", plain_content)

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully: {subject} to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.body}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    async def send_verification_email(
        self, to_email: str, verification_token: str, frontend_url: str
    ) -> bool:
        """
        Send email verification email

        Firebase equivalent: Part of registration flow
        """
        verification_link = f"{frontend_url}/auth/verify-email?token={verification_token}"

        subject = "Verify your email address"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Welcome! Please verify your email</h2>
                <p>Thank you for signing up. Please click the button below to verify your email address:</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Verify Email
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{verification_link}">{verification_link}</a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    If you didn't create an account, you can safely ignore this email.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        Welcome! Please verify your email
        
        Thank you for signing up. Please visit the following link to verify your email address:
        
        {verification_link}
        
        If you didn't create an account, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_password_reset_email(
        self, to_email: str, reset_token: str, frontend_url: str
    ) -> bool:
        """
        Send password reset email

        Firebase equivalent: Part of password reset flow
        """
        reset_link = f"{frontend_url}/auth/reset-password?token={reset_token}"

        subject = "Reset your password"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Reset your password</h2>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2196F3; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{reset_link}">{reset_link}</a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    This link will expire in 1 hour.<br>
                    If you didn't request a password reset, you can safely ignore this email.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        Reset your password
        
        We received a request to reset your password. Please visit the following link to create a new password:
        
        {reset_link}
        
        This link will expire in 1 hour.
        If you didn't request a password reset, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_magic_link_email(
        self, to_email: str, magic_token: str, frontend_url: str
    ) -> bool:
        """
        Send magic link for passwordless login

        Firebase equivalent: SendLinkToLoginUseCase
        """
        magic_link = f"{frontend_url}/auth/magic-link?token={magic_token}"

        subject = "Your login link"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Your login link is ready</h2>
                <p>Click the button below to log in to your account:</p>
                <p style="margin: 30px 0;">
                    <a href="{magic_link}" 
                       style="background-color: #9C27B0; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Log In
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{magic_link}">{magic_link}</a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    This link will expire in 15 minutes.<br>
                    If you didn't request this login link, you can safely ignore this email.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        Your login link is ready
        
        Click the following link to log in to your account:
        
        {magic_link}
        
        This link will expire in 15 minutes.
        If you didn't request this login link, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_invoice_email(
        self, to_email: str, invoice_number: str, invoice_pdf_url: str, amount: float, currency: str
    ) -> bool:
        """
        Send invoice email with PDF attachment link

        Firebase equivalent: IssueInvoiceToNewPaymentUseCase
        """
        subject = f"Invoice {invoice_number}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Your invoice is ready</h2>
                <p>Thank you for your payment. Your invoice is now available.</p>
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Invoice Number:</strong> {invoice_number}</p>
                    <p style="margin: 5px 0;"><strong>Amount:</strong> {amount:.2f} {currency.upper()}</p>
                </div>
                <p style="margin: 30px 0;">
                    <a href="{invoice_pdf_url}" 
                       style="background-color: #FF5722; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Download Invoice (PDF)
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{invoice_pdf_url}">{invoice_pdf_url}</a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    If you have any questions, please contact our support team.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        Your invoice is ready
        
        Thank you for your payment. Your invoice is now available.
        
        Invoice Number: {invoice_number}
        Amount: {amount:.2f} {currency.upper()}
        
        Download your invoice:
        {invoice_pdf_url}
        
        If you have any questions, please contact our support team.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_broadcast_email(
        self, to_email: str, title: str, message: str, url: Optional[str] = None
    ) -> bool:
        """
        Send broadcast/announcement email

        Firebase equivalent: BroadcastMessageUseCase
        """
        subject = title

        button_html = ""
        button_plain = ""
        if url:
            button_html = f"""
            <p style="margin: 30px 0;">
                <a href="{url}" 
                   style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Learn More
                </a>
            </p>
            """
            button_plain = f"\n\nLearn more: {url}\n"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>{title}</h2>
                <p style="line-height: 1.6;">{message}</p>
                {button_html}
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    You're receiving this because you're a registered user.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        {title}
        
        {message}
        {button_plain}
        
        You're receiving this because you're a registered user.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_payment_failed_email(
        self, to_email: str, amount: float, currency: str, retry_date: Optional[str] = None
    ) -> bool:
        """
        Send payment failed notification email

        Firebase equivalent: Part of HandleFailedPaymentUseCase
        """
        subject = "Payment Failed - Action Required"

        retry_info = ""
        if retry_date:
            retry_info = f"<p>We will automatically retry the payment on {retry_date}.</p>"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #d32f2f;">Payment Failed</h2>
                <p>We were unable to process your payment of <strong>{amount:.2f} {currency.upper()}</strong>.</p>
                
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ Your subscription may be affected</strong></p>
                    <p style="margin: 5px 0 0 0;">Please update your payment method to avoid service interruption.</p>
                </div>
                
                {retry_info}
                
                <p style="margin: 30px 0;">
                    <a href="{{billing_portal_url}}" 
                       style="background-color: #d32f2f; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Update Payment Method
                    </a>
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    Common reasons for payment failure:
                </p>
                <ul style="color: #666; font-size: 14px;">
                    <li>Insufficient funds</li>
                    <li>Expired card</li>
                    <li>Incorrect billing information</li>
                    <li>Card declined by bank</li>
                </ul>
                
                <p style="color: #666; font-size: 12px; margin-top: 40px;">
                    If you need assistance, please contact our support team.
                </p>
            </body>
        </html>
        """

        plain_content = f"""
        Payment Failed - Action Required
        
        We were unable to process your payment of {amount:.2f} {currency.upper()}.
        
        ⚠️ Your subscription may be affected
        Please update your payment method to avoid service interruption.
        
        {f'We will automatically retry the payment on {retry_date}.' if retry_date else ''}
        
        Common reasons for payment failure:
        - Insufficient funds
        - Expired card
        - Incorrect billing information
        - Card declined by bank
        
        Please update your payment method as soon as possible.
        
        If you need assistance, please contact our support team.
        """

        return await self.send_email(to_email, subject, html_content, plain_content)


# Singleton instance
email_service = EmailService()
