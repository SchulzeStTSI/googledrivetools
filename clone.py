from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import base64
import json
import argparse
import io
import common


def download_file(service, file_id,file_name, destination_folder,webLink, mimeType,properties):
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
    common.writeIndexEntry(webLink,path,mimeType,file_name,properties)

def clone_folder(service, source_folder_id, destination_folder_name,softClone,mime_Type):
    if not os.path.exists(destination_folder_name):
     os.mkdir(destination_folder_name)

    results = service.files().list(q=f"'{source_folder_id}' in parents",
                                    fields='files(id, name, mimeType, webContentLink,properties)').execute()
    items = results.get('files', [])

    for item in items:
        file_id = item['id']
        file_name = item['name']
        mimeType= item['mimeType']
        if 'properties' in item:
         properties = item['properties']
        else: 
         properties={}

        if mimeType != common.mimeType and (mime_Type != None and mime_Type != mimeType):
           continue

        if  mimeType != common.mimeType:
          webLink = item["webContentLink"]
          if not softClone:
             download_file(service,file_id,file_name,destination_folder_name,webLink, mimeType,properties)
          else:
            common.writeIndexEntry(webLink,"",mimeType,file_name,properties)
        else:
            clone_folder(service,file_id,os.path.join(destination_folder_name,file_name),softClone,mime_Type)

    print(f'Folder cloned successfully to {destination_folder_name}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    parser.add_argument("-sc", "--softClone", help="Just read filenames",default=True,action=argparse.BooleanOptionalAction)
    parser.add_argument("-mT", "--mimeType", help="mimeType which shall be considered",default=None)
    parser.add_argument("-coF", "--contentFolder", help="Content Folder where the index and the content is stored",default="content")

    common.addArgs(parser)
    args = parser.parse_args()
    
    service = common.configGoogleDrive(args)
  
    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        if "sourceFolder" not in d: 
            raise "No source folder given"
        else :
            source_folder_id = d["sourceFolder"]
        destination_folder_name = args.contentFolder
        clone_folder(service, source_folder_id, destination_folder_name,args.softClone, args.mimeType)

    common.writeIndex(args.contentFolder)
 