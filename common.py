from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import os
import json
import argparse

mimeType = 'application/vnd.google-apps.folder'

contentindexObjects =[]

def writeIndexEntry(weblink,path,mimeType,file_name,properties,file_id,folder_id,folders):
    o = {
        "id": file_id,
        "webLink":weblink,
        "path": path,
        "mimeType":mimeType,
        "fileName":file_name,
        "folder":folder_id,
        "properties": properties,
        "folders": folders,
    }      
    contentindexObjects.append(o)


def writeIndex(contentfolder):
   index = open(contentfolder+"/index", "w")
   contentIndex = {
       "indexObjects": contentindexObjects
   }
   json_object = json.dumps(contentIndex, indent=4)
   index.write(json_object)
   index.close()

def addArgs(parser):
    parser.add_argument("-sAF", "--serviceAccountFile", help="Google Drive Service Account File",default=None)

def configGoogleDrive(args):
    
    service_account_file = os.path.join("tmp", "google_service_account.json")

    if args.serviceAccountFile != None:
        service_account_file = args.serviceAccountFile

    if os.environ.get("GOOGLE_SERVICE_ACCOUNT") is not None:
        jsonDecoded = base64.b64decode(os.environ.get("GOOGLE_SERVICE_ACCOUNT"))    
        with open(service_account_file,"wb") as f:
            f.write(jsonDecoded)

    creds = service_account.Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    return service
