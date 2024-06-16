from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import os

mimeType = 'application/vnd.google-apps.folder'


def configGoogleDrive(serviceAccountFile):

    service_account_file = os.path.join("tmp", "google_service_account.json")
 
    if serviceAccountFile != None:
        service_account_file = serviceAccountFile

    if os.environ.get("GOOGLE_SERVICE_ACCOUNT") is not None:
        jsonDecoded = base64.b64decode(os.environ.get("GOOGLE_SERVICE_ACCOUNT"))    
        with open(service_account_file,"wb") as f:
            f.write(jsonDecoded)

    creds = service_account.Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    return service
