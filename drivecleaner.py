import common
import json
import argparse
from dateutil import parser
import os
from datetime import datetime

def clone_folder(service, source_folder_id,mime_Type):

    results = service.files().list(q=f"'{source_folder_id}' in parents",
                                    fields='files(id, mimeType,properties)').execute()
    items = results.get('files', [])

    for item in items:
        file_id = item['id']
        mimeType= item['mimeType']
        if 'properties' in item:
         properties = item['properties']
        else: 
         properties={}

        if  mimeType != common.mimeType and properties != {}:
         
         parsed_date = parser.isoparse(properties["expire"])
         current_date = datetime.now()

         if parsed_date < current_date:
                try:
                    service.files().delete(fileId=file_id).execute()
                    print('Datei erfolgreich gelöscht.')
                except Exception as e:
                    print(f'Fehler beim Löschen der Datei: {e}')
        else:
            clone_folder(service,file_id,mime_Type)

    print(f'Folder cleaned successfully to {source_folder_id}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    common.addArgs(parser)
    args = parser.parse_args()

    service = common.configGoogleDrive(args)

    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        if "sourceFolder" not in d: 
            raise "No source folder given"
        else :
            source_folder_id = d["sourceFolder"]
    clone_folder(service, source_folder_id, args.mimeType)
