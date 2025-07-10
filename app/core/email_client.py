import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from .config import get_email_config


class EmailManager:
    """Email client manager using aiosmtplib"""
    
    def __init__(self):
        self.config = get_email_config()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send an email"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            if cc:
                message["Cc"] = ", ".join(cc)
            
            # Add body
            if html_body:
                # Create both plain text and HTML parts
                text_part = MIMEText(body, "plain")
                html_part = MIMEText(html_body, "html")
                message.attach(text_part)
                message.attach(html_part)
            else:
                text_part = MIMEText(body, "plain")
                message.attach(text_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment['filename']}"
                    )
                    message.attach(part)
            
            # Prepare recipients
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.config.smtp_host,
                port=self.config.smtp_port,
                username=self.config.username,
                password=self.config.password,
                use_tls=self.config.use_tls,
                use_ssl=self.config.use_ssl,
                recipients=recipients
            )
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_simple_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send a simple text email"""
        return await self.send_email(to_email, subject, body)
    
    async def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an HTML email with optional text fallback"""
        if text_body is None:
            # Simple HTML to text conversion
            import re
            text_body = re.sub(r'<[^>]+>', '', html_body)
            text_body = re.sub(r'\s+', ' ', text_body).strip()
        
        return await self.send_email(to_email, subject, text_body, html_body)
    
    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        notification_type: str = "info"
    ) -> bool:
        """Send a notification email with HTML template"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }}
                .notification-{notification_type} {{ border-left: 4px solid #007bff; padding-left: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{subject}</h2>
                </div>
                <div class="content notification-{notification_type}">
                    {message}
                </div>
                <div class="footer">
                    <p>This is an automated message from OCR Identity API.</p>
                    <p>If you have any questions, please contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_html_email(to_email, subject, html_template, message)
    
    async def test_connection(self) -> bool:
        """Test email connection"""
        try:
            # Create a simple test message
            message = MIMEText("Test email from OCR Identity API")
            message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            message["To"] = self.config.from_email
            message["Subject"] = "Test Connection"
            
            await aiosmtplib.send(
                message,
                hostname=self.config.smtp_host,
                port=self.config.smtp_port,
                username=self.config.username,
                password=self.config.password,
                use_tls=self.config.use_tls,
                use_ssl=self.config.use_ssl,
                recipients=[self.config.from_email]
            )
            return True
            
        except Exception as e:
            print(f"Email connection test failed: {e}")
            return False


# Global email manager instance
email_manager = EmailManager()


def get_email() -> EmailManager:
    """Get the email manager instance"""
    return email_manager


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """Convenience function to send email"""
    return await email_manager.send_email(to_email, subject, body, html_body) 