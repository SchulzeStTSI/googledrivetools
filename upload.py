
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaIoBaseUpload
import os
import argparse
import json
import common
import mimetypes
from pathlib import Path

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


def upload_folder(service,source_folder_name, destination_id,parent_id,media_type,root,folders):
    if not os.path.exists(source_folder_name):
     os.mkdir(source_folder_name)

    folder_name = os.path.basename(source_folder_name)
    if parent_id and root:
        folder_id = parent_id
    else:
       folder_id = create_folder(service, folder_name, destination_id)
   
    root = False
    print("Scan Directory: "+source_folder_name)
    for item in os.listdir(source_folder_name):
        print("Upload: "+item)
        newArray=[folder_id]
        item_path = os.path.join(source_folder_name, item)
        if os.path.isdir(item_path):
            upload_folder(service, item_path, folder_id,media_type,root,folders+newArray)
        else:
            upload_file(service, item_path, folder_id,media_type,folders+newArray)
     

def upload_file(service,file_path, folder_id,media_type,folders):

    mime_type = get_mime_type(file_path)

    if media_type != None and media_type != mime_type:
        print("Skip file "+file_path+" because mimetype was not "+media_type+".Actual type was "+mime_type)
        return
    
    base_name, _ = os.path.splitext(file_path)
    path = base_name + ".json" 
    
    if os.path.isfile(path) and os.access(path, os.R_OK):
       r = open(path,"r")
       properties= json.load(r)
    else:
       properties={}

    with open(file_path, 'rb') as file:
        file_metadata = {'name': os.path.basename(file_path),'parents': [folder_id], "properties": properties}
        media = MediaIoBaseUpload(file, mimetype=mime_type)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file = service.files().get(fileId=file.get('id'), fields='id, webContentLink, name').execute()

        print(f'File ID: {file.get("id")}')
        print(f'Web Content Link: {file.get("webContentLink")}')
        common.writeIndexEntry(file.get("webContentLink"),file_path,mime_type,file.get("name"),properties,file.get("id"),folder_id,folders)


if __name__ == "__main__":
    print("Start Upload")
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    parser.add_argument("-uF", "--uploadFolder", help="Uploads the entire folder to drive",default="content")
    parser.add_argument("-pid", "--parentid", help="parentid",default=None)
    parser.add_argument("-mT", "--mediaType", help="Media Type which shall be uploaded",default=None)

    common.addArgs(parser)
    args = parser.parse_args()
    service = common.configGoogleDrive(args)

    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        if "destinationFolder" not in d:
              raise "No destination folder given"
        else:
           destination_folder_id = d["destinationFolder"]
        
        source_folder_name = args.uploadFolder
        if args.parentid == None:
            args.parentid = destination_folder_id
        folders=[destination_folder_id]
        upload_folder(service, source_folder_name, destination_folder_id,args.parentid,args.mediaType,True,folders)