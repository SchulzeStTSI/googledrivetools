from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import base64
import json
import argparse
import io

mimeType = 'application/vnd.google-apps.folder'


def download_file(service, file_id,file_name, destination_folder):
    path = os.path.join(destination_folder, file_name)
    if os.path.exists(path):
        return

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {file_name} {int(status.progress() * 100)}%.")

def clone_folder(service, source_folder_id, destination_folder_name):
    if not os.path.exists(destination_folder_name):
     os.mkdir(destination_folder_name)

    results = service.files().list(q=f"'{source_folder_id}' in parents",
                                    fields='files(id, name, mimeType)').execute()
    items = results.get('files', [])

    for item in items:
        file_id = item['id']
        file_name = item['name']
        if item['mimeType'] != mimeType:
          download_file(service,file_id,file_name,destination_folder_name)
        else:
            clone_folder(service,file_id,os.path.join(destination_folder_name,file_name))

    print(f'Folder cloned successfully to {destination_folder_name}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    parser.add_argument("-sAF", "--serviceAccountFile", help="Google Drive Service Account File",default=None)
    
    args = parser.parse_args()
    service_account_file = os.path.join("tmp", "google_service_account.json")
 
    if args.serviceAccountFile != None:
        service_account_file = args.serviceAccountFile

    if os.environ.get("GOOGLE_SERVICE_ACCOUNT") is not None:
        jsonDecoded = base64.b64decode(os.environ.get("GOOGLE_SERVICE_ACCOUNT"))    
        with open(service_account_file,"wb") as f:
            f.write(jsonDecoded)

    creds = service_account.Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)

    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        source_folder_id = d["sourceFolder"]
        destination_folder_name = 'content'
        clone_folder(service, source_folder_id, destination_folder_name)
