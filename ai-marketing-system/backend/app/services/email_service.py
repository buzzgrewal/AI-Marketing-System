import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.campaign import EmailLog
from app.models.lead import Lead


class EmailService:
    """Service for sending emails to opted-in contacts"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = True,
        campaign_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Send an individual email"""

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add unsubscribe header for compliance
            if campaign_id:
                unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe?email={to_email}"
                message["List-Unsubscribe"] = f"<{unsubscribe_url}>"

            # Attach body
            if is_html:
                # Add plain text version for better deliverability
                plain_text = self._html_to_plain(body)
                part1 = MIMEText(plain_text, "plain")
                part2 = MIMEText(body, "html")
                message.attach(part1)
                message.attach(part2)
            else:
                part = MIMEText(body, "plain")
                message.attach(part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            # Log email if database session provided
            if db and campaign_id and lead_id:
                email_log = EmailLog(
                    campaign_id=campaign_id,
                    lead_id=lead_id,
                    recipient_email=to_email,
                    subject=subject,
                    status="sent",
                    sent_at=datetime.utcnow()
                )
                db.add(email_log)
                db.commit()

            return True

        except Exception as e:
            # Log error
            if db and campaign_id and lead_id:
                email_log = EmailLog(
                    campaign_id=campaign_id,
                    lead_id=lead_id,
                    recipient_email=to_email,
                    subject=subject,
                    status="failed",
                    error_message=str(e),
                    sent_at=datetime.utcnow()
                )
                db.add(email_log)
                db.commit()

            print(f"Error sending email to {to_email}: {str(e)}")
            return False

    async def send_bulk_email(
        self,
        recipients: List[dict],
        subject: str,
        body: str,
        campaign_id: int,
        db: Session
    ) -> dict:
        """Send emails to multiple recipients"""

        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0
        }

        for recipient in recipients:
            success = await self.send_email(
                to_email=recipient["email"],
                subject=subject,
                body=body,
                campaign_id=campaign_id,
                lead_id=recipient.get("lead_id"),
                db=db
            )

            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1

        return results

    def _html_to_plain(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # Remove HTML tags (basic implementation)
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()

    def create_email_template(
        self,
        content: str,
        unsubscribe_link: bool = True
    ) -> str:
        """Create a basic HTML email template"""

        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center; background-color: #2c3e50;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px;">Premier Bike & Position One Sports</h1>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            {content}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background-color: #ecf0f1; font-size: 12px; color: #7f8c8d;">
                            <p style="margin: 0 0 10px 0;">
                                <a href="https://premierbike.com" style="color: #3498db; text-decoration: none;">premierbike.com</a> |
                                <a href="https://positiononesports.com" style="color: #3498db; text-decoration: none;">positiononesports.com</a>
                            </p>
                            {'''<p style="margin: 10px 0 0 0;">
                                <a href="{{unsubscribe_url}}" style="color: #7f8c8d; text-decoration: underline;">Unsubscribe</a>
                            </p>''' if unsubscribe_link else ''}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return template


# Singleton instance
email_service = EmailService()
