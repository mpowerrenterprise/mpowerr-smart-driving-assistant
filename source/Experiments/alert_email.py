import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
EMAIL_ADDRESS = "nithushannithu035@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "nithu@321"  # Replace with your email password
RECIPIENT_EMAIL = "nithushan014@gmail.com"  # Replace with recipient's email

def send_email():
    """Send an email alert about drowsiness detection."""
    try:
        print("Preparing the email content...")
        
        # Create email content
        subject = "Drowsiness Alert!"
        body = "The system has detected drowsiness. Please take necessary action."
        
        # Set up the email structure
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        print("Email content prepared successfully.")

        print("Connecting to the SMTP server...")
        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("Starting TLS encryption...")
            server.starttls()  # Upgrade connection to secure
            
            print("Logging in to the email account...")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in to email account
            
            print("Sending the email...")
            server.send_message(msg)  # Send the email
            
        print("Drowsiness alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Call the function to send the email
send_email()
