import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Any
from app.utils.config import ENV_PROJECT


def format_value(value):
    try:
        if value is None:
            return "<i>No data</i>"
        if isinstance(value, (dict, list)):
            formatted = json.dumps(value, indent=2)
            return f"<pre style='background:#f3f4f6;padding:10px;border-radius:6px;'>{formatted}</pre>"
        if isinstance(value, list):
            formatted_items = "".join(
                f"<li style='margin-bottom:4px;'>{str(item)}</li>" for item in value
            )
            return f"<ul style='background:#f3f4f6;padding:10px;border-radius:6px;list-style-type:disc;'>{formatted_items}</ul>"
        return f"<p style='background:#f9fafb;padding:10px;border-radius:6px;'>{str(value)}</p>"
    except Exception:
        return f"<p>{str(value)}</p>"


async def send_approval_email(
    email: str, token: str, response: Any, expected_output: Any
):
    html_response = format_value(response)
    html_expected = format_value(expected_output)

    html_content = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color:#1e3a8a;">Approval Needed</h2>
        <p>Please review the following details before approving:</p>

        <div style="background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; padding:15px; margin-top:10px;">
            <h3 style="color:#111827;">Response:</h3>
            {html_response}

            <h3 style="color:#111827;">Expected Output:</h3>
            {html_expected}
        </div>

        <p style="margin-top:20px;">Click below to review and approve:</p>
        <a href="http://localhost:8001/api/approval/response_approval?token={token}&isvalid=true"
        style="display:inline-block;background:#16a34a;color:white;
          padding:10px 20px;text-decoration:none;border-radius:6px;
          font-weight:bold;margin-right:10px;">
            Approve
        </a>

        <a href="http://localhost:8001/api/approval/response_approval?token={token}&isvalid=false"
            style="display:inline-block;background:#dc2626;color:white;
            padding:10px 20px;text-decoration:none;border-radius:6px;
            font-weight:bold;">
        Reject
        </a>

        <p style="margin-top:20px; color:#6b7280; font-size:12px;">
            If you don't expect this email, you can safely ignore it.
        </p>
    </div>
    """

    message = MIMEMultipart("alternative")
    message["From"] = ENV_PROJECT.SUPERADMIN_EMAILID
    message["To"] = email
    message["Subject"] = "Approval Needed"
    message.attach(MIMEText(html_content, "html"))

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=ENV_PROJECT.SUPERADMIN_EMAILID,
        password=ENV_PROJECT.MAIL_PASSWORD,
    )
