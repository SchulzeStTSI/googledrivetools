
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaIoBaseUpload
import os
import argparse
import json
import common
import mimetypes

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


def create_folder(service, name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': common.mimeType
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def upload_folder(service,source_folder_name, parent_id, index):
    if not os.path.exists(source_folder_name):
     os.mkdir(source_folder_name)

    folder_name = os.path.basename(source_folder_name)
    folder_id = create_folder(service, folder_name, parent_id)

    for item in os.listdir(source_folder_name):
        item_path = os.path.join(source_folder_name, item)
        if os.path.isdir(item_path):
            upload_folder(service, item_path, folder_id,index)
        else:
            upload_file(service, item_path, folder_id,index)
     

def upload_file(service,file_path, folder_id,index):

    mime_type = get_mime_type(file_path)

    with open(file_path, 'rb') as file:
        file_metadata = {'name': os.path.basename(file_path),'parents': [folder_id]}
        media = MediaIoBaseUpload(file, mimetype=mime_type)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f'File ID: {file.get("id")}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    parser.add_argument("-sAF", "--serviceAccountFile", help="Google Drive Service Account File",default=None)
    parser.add_argument("-uF", "--uploadFolder", help="Uploads the entire folder to drive",default="blub")
    args = parser.parse_args()
    service = common.configGoogleDrive(args.serviceAccountFile)
  
    index = open("index", "w")

    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        destination_folder_id = d["destinationFolder"]
        source_folder_name = args.uploadFolder
        upload_folder(service, source_folder_name, destination_folder_id,index)

    index.close()