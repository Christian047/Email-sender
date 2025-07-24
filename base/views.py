
from django.urls import reverse
from django.shortcuts import redirect
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import Template, Context
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


import re

from django.shortcuts import redirect
from urllib.parse import urlencode
load_dotenv()


def home(request):
    """Homepage that can redirect to login with email prefilled"""
    email = request.GET.get('email')
    print(f"Home view: email={email}")
    if email and email.strip():  # Check for non-empty email
        login_url = f"{reverse('login')}?email={email}"
        print(f"Redirecting to: {login_url}")
        return redirect(login_url)
    return render(request, 'index.html')


def login_view(request):
    """Login view with email prefilling support"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Add authentication logic here
        return redirect('home')
    
    email = request.GET.get('email', '')
    context = {
        'prefilled_email': email,
    }
    return render(request, 'login.html', context)





def download_invoice(request):
    """Handle invoice download with proper redirection"""
    email = request.GET.get('email')
    if email and email.strip():  # Ensure email is non-empty
        print(f"Invoice download requested for: {email}")
        return redirect(f"{reverse('login')}?email={email}")
    
    print("No email provided, redirecting to login")
    return redirect('login')




def myhome(request):
    return render(request, 'home.html')


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_bulk_email(request):
    if request.method == 'POST':
        recipients = request.POST.get('recipients', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_template = request.POST.get('message', '').strip()  # This now comes hardcoded from frontend
        sender_name = request.POST.get('sender_name', '').strip()
        email_type = request.POST.get('email_type', 'plain')
        
        if not recipients or not subject or not message_template:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'email_sender.html')
        
        email_list = []
        for email in recipients.replace(';', ',').replace('\n', ',').split(','):
            email = email.strip()
            if email and validate_email(email):
                email_list.append(email)
        
        if not email_list:
            messages.error(request, 'Please provide valid email addresses.')
            return render(request, 'email_sender.html')
        
        success_count = 0
        failed_emails = []
        
        for recipient in email_list:
            try:
                # Since template is now hardcoded from frontend, just replace the email placeholder
                personalized_message = message_template.replace('RECIPIENT_EMAIL_PLACEHOLDER', recipient)
                
                send_individual_email(
                    recipient=recipient,
                    subject=subject,
                    body=personalized_message,
                    sender_name=sender_name,
                    is_html=(email_type == 'html')
                )
                
                success_count += 1
                
            except Exception as e:
                failed_emails.append(f"{recipient}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f'Successfully sent {success_count} emails!')
        
        if failed_emails:
            messages.error(request, f'Failed to send to: {", ".join(failed_emails)}')
        
        return render(request, 'email_sender.html')
    
    return render(request, 'email_sender.html')



def send_individual_email(recipient, subject, body, sender_name='', is_html=False):
    """
    Send individual email with HTML support and better error handling
    """
    print(f"[EMAIL] Starting email send process...")
    print(f"[EMAIL] Recipient: {recipient}")
    print(f"[EMAIL] Subject: {subject}")
    print(f"[EMAIL] Sender name: {sender_name if sender_name else 'Not specified'}")
    print(f"[EMAIL] HTML format: {is_html}")
    
    # Get email credentials from environment variables
    print("[EMAIL] Loading credentials from environment variables...")
    print(f"[EMAIL] Current working directory: {os.getcwd()}")
    
    # Check if .env file exists
    env_file_path = os.path.join(os.getcwd(), '.env')
    print(f"[EMAIL] Looking for .env file at: {env_file_path}")
    print(f"[EMAIL] .env file exists: {os.path.exists(env_file_path)}")
    
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"[EMAIL] EMAIL_SENDER from env: {email_sender}")
    print(f"[EMAIL] EMAIL_PASSWORD from env: {email_password}")
    
    # Check if credentials are available
    if not email_sender or not email_password:
        print("[EMAIL] ERROR: Credentials not found in environment variables!")
        print("[EMAIL] Available environment variables:")
        for key in os.environ.keys():
            if 'EMAIL' in key.upper():
                print(f"[EMAIL]   {key}: {os.environ[key] if 'PASSWORD' not in key.upper() else '*' * len(os.environ[key])}")
        raise Exception("Email credentials not found. Please check your .env file.")
    
    print(f"[EMAIL] Using sender email: {email_sender}")
    print("[EMAIL] Password loaded successfully (hidden)")
    
    try:
        print("[EMAIL] Creating email message...")
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f'{sender_name} <{email_sender}>' if sender_name else email_sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        print(f"[EMAIL] Message headers configured:")
        print(f"[EMAIL]   From: {msg['From']}")
        print(f"[EMAIL]   To: {msg['To']}")
        print(f"[EMAIL]   Subject: {msg['Subject']}")
        
        # Attach body (HTML or plain text)
        print("[EMAIL] Attaching message body...")
        if is_html:
            msg.attach(MIMEText(body, 'html'))
            print("[EMAIL] Body attached as HTML")
        else:
            msg.attach(MIMEText(body, 'plain'))
            print("[EMAIL] Body attached as plain text")
        
        # Send email with better error handling
        print("[EMAIL] Establishing SMTP connection...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            print("[EMAIL] SMTP connection established successfully")
            print("[EMAIL] Attempting to login...")
            smtp.login(email_sender, email_password)
            print("[EMAIL] Login successful!")
            
            print("[EMAIL] Sending email...")
            smtp.sendmail(email_sender, recipient, msg.as_string())
            print("[EMAIL] Email sent successfully!")
            
    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] ERROR: Authentication failed!")
        raise Exception("Email authentication failed. Check credentials.")
    except smtplib.SMTPRecipientsRefused:
        print("[EMAIL] ERROR: Recipient email was refused!")
        raise Exception("Recipient email address was refused.")
    except smtplib.SMTPServerDisconnected:
        print("[EMAIL] ERROR: SMTP server disconnected!")
        raise Exception("SMTP server disconnected unexpectedly.")
    except Exception as e:
        print(f"[EMAIL] ERROR: Unexpected error occurred: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
    
    print("[EMAIL] Email sending process completed successfully!")



@csrf_exempt
def get_invoice_template(request):
    """View to provide pre-built invoice email template with working links"""
    if request.method == 'GET':
        template_type = request.GET.get('type', 'invoice')
        
        if template_type == 'invoice':
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice Due for Payment</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #2a2a2a;
            border-radius: 8px;
            padding: 0;
            overflow: hidden;
        }
        .header {
            background-color: #333333;
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #444444;
        }
        .header h1 {
            margin: 0;
            color: #ffffff;
            font-size: 24px;
            font-weight: normal;
        }
        .content {
            padding: 30px;
        }
        .invoice-info {
            background-color: #333333;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }
        .invoice-info h2 {
            margin: 0 0 20px 0;
            color: #ffffff;
            font-size: 18px;
        }
        .invoice-info p {
            margin: 0;
            color: #cccccc;
            line-height: 1.5;
        }
        .attachment {
            background-color: #1a1a1a;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
            border: 1px solid #444444;
        }
        .attachment-name {
            color: #4a9eff;
            font-weight: bold;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            padding: 8px 16px;
            background-color: #333333;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .attachment-name:hover {
            background-color: #555555;
            color: #ffffff;
        }
        .footer {
            background-color: #1a1a1a;
            padding: 15px;
            text-align: center;
            border-top: 1px solid #444444;
        }
        .footer a {
            color: #4a9eff;
            text-decoration: none;
            font-size: 12px;
            margin: 0 5px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .sender-info {
            color: #cccccc;
            font-size: 12px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Invoice Due for Payment</h1>
        </div>
        
        <div class="content">
            <div class="sender-info">
                From: {{ sender_name }} | To: {{ recipient_name }}
            </div>
            
            <div class="invoice-info">
                <h2>Important Invoice Information from Accounts</h2>
                <p>Please note that invoices highlighted in red are overdue, while those in green have been paid.</p>
            </div>
            
            <div class="attachment">
                <a href="{{ download_url }}?email={{ recipient_email }}" class="attachment-name">📄 Overdue_and_Paid_Invoices_2025.pdf</a>
            </div>
            
            <p style="color: #cccccc; text-align: center; margin-top: 30px;">
                Please review your invoice status and make payments for any overdue amounts.
            </p>
        </div>
        
        <div class="footer">
            <a href="{{ unsubscribe_url }}">Unsubscribe</a> | 
            <a href="{{ base_url }}contact/">Contact Support</a>
        </div>
    </div>
</body>
</html>
            """
            
            return JsonResponse({
                'template': html_template,
                'subject': 'Invoice Due for Payment',
                'type': 'html'
            })
    
    return JsonResponse({'error': 'Invalid request'})




def unsubscribe(request):
    """Handle unsubscribe requests"""
    email = request.GET.get('email')
    if email:
        # Here you would typically add the email to an unsubscribe list
        print(f"Unsubscribe requested for: {email}")
        return render(request, 'unsubscribe_success.html', {'email': email})
    return render(request, 'unsubscribe_error.html')

def contact_support(request):
    """Contact support page"""
    return render(request, 'contact_support.html')

# Alternative: Django-native approach with HTML support
def send_bulk_email_django_native(request):
    """
    Enhanced Django-native email sending with HTML support
    """
    if request.method == 'POST':
        recipients = request.POST.get('recipients', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_template = request.POST.get('message', '').strip()
        sender_name = request.POST.get('sender_name', '').strip()
        email_type = request.POST.get('email_type', 'plain')
        
        # Validate inputs
        if not recipients or not subject or not message_template:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'email_sender.html')
        
        # Process recipients with better validation
        email_list = []
        for email in recipients.replace(';', ',').replace('\n', ',').split(','):
            email = email.strip()
            if email and validate_email(email):
                email_list.append(email)
        
        if not email_list:
            messages.error(request, 'Please provide valid email addresses.')
            return render(request, 'email_sender.html')
        
        # Send emails using Django's EmailMessage
        success_count = 0
        failed_emails = []
        
        for recipient in email_list:
            try:
                # Create template context with proper URLs
                context = Context({
                    'recipient_email': recipient,
                    'sender_name': sender_name,
                    'recipient_name': recipient.split('@')[0].title(),
                    'base_url': request.build_absolute_uri('/'),
                    'unsubscribe_url': request.build_absolute_uri(f'/unsubscribe/?email={recipient}'),
                    'download_url': request.build_absolute_uri('/download/invoice/'),
                })
                
                # Render template
                template = Template(message_template)
                rendered_message = template.render(context)
                
                # Create and send email
                email = EmailMessage(
                    subject=subject,
                    body=rendered_message,
                    from_email=f'{sender_name} <{settings.DEFAULT_FROM_EMAIL}>' if sender_name else settings.DEFAULT_FROM_EMAIL,
                    to=[recipient],
                )
                
                # Set content type for HTML emails
                if email_type == 'html':
                    email.content_subtype = 'html'
                
                email.send()
                success_count += 1
                
            except Exception as e:
                failed_emails.append(f"{recipient}: {str(e)}")
        
        # Show results
        if success_count > 0:
            messages.success(request, f'Successfully sent {success_count} emails!')
        
        if failed_emails:
            messages.error(request, f'Failed to send to: {", ".join(failed_emails)}')
        
        return render(request, 'email_sender.html')
    
    return render(request, 'email_sender.html')