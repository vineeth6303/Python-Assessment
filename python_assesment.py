import gspread
from google.oauth2 import service_account
import googlemaps
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

def authenticate_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_file(
        'your-service-account-key.json',
        scopes=scopes
    )
    gc = gspread.authorize(credentials)
    return gc
def authenticate_google_maps(api_key):
    gmaps = googlemaps.Client(key=api_key)
    return gmaps

def authenticate_chatgpt(api_key):
    openai.api_key = api_key

def fetch_leads(gmaps, location):
    places = gmaps.places_nearby(location, radius=1000, type='restaurant')  # Change 'restaurant' to your target business type
    leads = []

    for place in places['results']:
        lead = {
            'Name': place['Its me'],
            'Address': place['vicinity'],
            'Phone': place.get('formatted_phone_number', 'N/A'),
            'Website': place.get('website', 'N/A')
        }
        leads.append(lead)

    return leads

def send_email(recipient, subject, message, attachments=[]):
    smtp_server = 'smtp.your-email-provider.com'
    smtp_port = 587
    smtp_username = 'your-email@example.com'
    smtp_password = 'your-email-password'

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))


        for attachment in attachments:
            with open(attachment, 'rb') as file:
                part = MIMEApplication(file.read())
                part.add_header('Content-Disposition', f'attachment; filename="{attachment}"')
                msg.attach(part)

        server.sendmail(smtp_username, recipient, msg.as_string())
        print(f"Email sent to {recipient}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")

    finally:
        server.quit()

def main():

    authenticate_google_sheets()
    gmaps = authenticate_google_maps('your-google-maps-api-key')
    authenticate_chatgpt('your-chatgpt-api-key')


    location = 'New York, NY'


    leads = fetch_leads(gmaps, location)


    gc = authenticate_google_sheets()
    spreadsheet = gc.open('Leads')
    worksheet = spreadsheet.sheet1

    for lead in leads:
        worksheet.append_table([lead['Name'], lead['Address'], lead['Phone'], lead['Website']])


    for lead in leads:
        recipient = 'recipient@example.com'  # Change to the recipient's email
        subject = 'Your Subject'
        message = f"Hello {lead['Name']},\n\nThis is a personalized message for your business at {lead['Address']}."


        attachments = []

        send_email(recipient, subject, message, attachments)

if __name__ == '__main__':
    main()
