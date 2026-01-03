import html2text
from django.template.loader import render_to_string
from loguru import logger


class EmailNotificationService:
    def send_email(self, subject: str, html_template_path: str, to_email: list[str], context: dict):
        html_content = render_to_string(html_template_path, context)
        
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        text_content = h.handle(html_content)
        
        output = []
        output.append("=" * 80)
        output.append("EMAIL NOTIFICATION")
        output.append("=" * 80)
        output.append(f"To: {', '.join(to_email)}")
        output.append(f"Subject: {subject}")
        output.append("-" * 80)
        output.append("HTML VERSION:")
        output.append("-" * 80)
        output.append(html_content)
        output.append("-" * 80)
        output.append("TEXT VERSION:")
        output.append("-" * 80)
        output.append(text_content)
        output.append("=" * 80)
        
        logger.opt(raw=True).info("\n".join(output) + "\n")

