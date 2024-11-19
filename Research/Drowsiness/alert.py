from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

# Message details
message = client.messages.create(
    body="Hello, this is a test message from Twilio!",
    from_='+1234567890',  # Replace with your Twilio number
    to='+0987654321'       # Replace with the recipient's phone number
)

print(f"Message sent with SID: {message.sid}")
