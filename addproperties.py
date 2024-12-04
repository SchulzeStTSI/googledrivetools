import common
import json
import os
import argparse
import glob
from pathlib import Path

class fileItem: 
    id: any
    name: any
    properties: any


def findFiles(service,source_folder_id):
    results = service.files().list(q=f"'{source_folder_id}' in parents",
                                    fields='files(id, name, mimeType, webContentLink,properties)').execute()
    items = results.get('files', [])
    files=[]
    for item in items:
        i = fileItem()

        i.id = item['id']
        i.name= item['name']
        mimeType = item['mimeType']

        if 'properties' in item:
             i.properties = item['properties']
        else: 
             i.properties={}

        if  mimeType == common.mimeType:
            newFiles=findFiles(service,i.id)
            for i in newFiles:
                files.append(i)
        else: 
            files.append(i)

    return files

def addProperties(service,source_folder_id,scanfolder):
   
    items=findFiles(service,source_folder_id)

    files= glob.glob(scanfolder+"/*.json")
    baseFiles=[]
    for i in files:
        basename = os.path.basename(i)
        baseFiles.append(basename)

    for item in items:
        file_name= Path(item.name).stem +".json"

        if file_name in baseFiles:
            f = open(os.path.join(scanfolder,file_name))
            data = json.load(f)
            if len(data) >0:
                updated_file = service.files().update(
                    fileId=item.id,
                    body=data,
                    fields='properties'
                ).execute()
                file = service.files().get(fileId=item.id, fields='id, properties').execute()
                print(file)
        
        


if __name__ == "__main__":
    print("Start Add Properties")
    parser = argparse.ArgumentParser()
    parser.add_argument("-cF", "--configFolder", help="Config Folder",default="./config")
    parser.add_argument("-dF", "--descriptorFolder", help="Folder where are the descriptors of a file",default="./desc")
    common.addArgs(parser)
    args = parser.parse_args()

    service = common.configGoogleDrive(args)

    with open(os.path.join(args.configFolder,'googledrive.json')) as f:
        d = json.load(f)
        if "sourceFolder" not in d: 
            raise "No source folder given"
        else :
            source_folder_id = d["sourceFolder"]
        addProperties(service,source_folder_id,args.descriptorFolder)