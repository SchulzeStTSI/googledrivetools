import common
import json
import argparse
import os
from datetime import datetime
from pytz import timezone

def clone_folder(service, source_folder_id):

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

        if  mimeType != common.mimeType:   
         if  properties != {}:
            parsed_date = datetime.fromisoformat(properties["expire"])
            current_date = datetime.now().astimezone(timezone('UTC'))

            if parsed_date < current_date:
                    try:
                        service.files().delete(fileId=file_id).execute()
                        print('Datei erfolgreich gelöscht.')
                    except Exception as e:
                        print(f'Fehler beim Löschen der Datei: {e}')
        else:
            clone_folder(service,file_id)

    print(f'Folder cleaned successfully to {source_folder_id}')


if __name__ == "__main__":
    print("Start Drive Clean")
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
    clone_folder(service, source_folder_id)
