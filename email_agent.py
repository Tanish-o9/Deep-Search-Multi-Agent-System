import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from agents import Agent, function_tool
from agents.model_settings import ModelSettings
from ollama_model import MODEL

load_dotenv(override=True)

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
EMAIL_APP_PASSWORD= os.getenv('EMAIL_APP_PASSWORD')

if EMAIL_ADDRESS:
    print('Email address is set.')
else:
    print('Email address is not set.')

if EMAIL_SMTP_SERVER:
    print('Email STMP server is set.')
else:
    print('Email STMP server is not set.')

if EMAIL_APP_PASSWORD:
    print('Password is set.')
else:
    print('Password address is not set.')

@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
    """
    Send out an email with the given subject and body to all sales prospects
    
    Args:
        subject: The subject of the email
        text_body: The body of the email as plain text
        html_body: The HTML body of the email
    """
    msg= EmailMessage()
    msg['From']= EMAIL_ADDRESS
    msg['To']= EMAIL_ADDRESS
    msg['Subject']= subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype= 'html')

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)

INSTRUCTIONS = """
You will receive a research report in markdown. Convert it to a clean HTML email and send it using send_email_tool. Always call the tool — never just describe the email.

Rules:
- Subject line: specific to the report's topic, not generic.
- Keep all facts, numbers, and claims unchanged.
- Only include a link if a real URL appears in the source. Never invent or use placeholder URLs (e.g. example.com).
- If a table is broken (mismatched columns, mostly empty cells), convert it to a bulleted list instead.
- Use simple HTML: headings, paragraphs, bold, bullet lists. No complex CSS.
- Plain-text body must be a full readable version of the content, not a one-line teaser.
"""

email_agent = Agent(
    name="Email Agent",
    instructions=INSTRUCTIONS,
    tools=[send_email_tool],
    model_settings=ModelSettings(tool_choice="required"),
    model=MODEL
)

print('succeeded')