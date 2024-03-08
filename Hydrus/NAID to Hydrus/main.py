import os
import json
import exiftool
import hydrus_api
import hydrus_api.utils
regularImport = ""
importingFiles = []
currentTagList = []
importPath = ""
client = None;
servicekey = ""
config = None
try:
    config = open("config.json", "r+")
except:
    config = open("config.json", "w+")
    config.write("")
    config.close()
    config = open("config.json", "r+")
def mainMenu(inp = None):
    global regularImport
    global importPath
    global client
    global servicekey
    if inp == None:
        global regularImport
        regularImport = input("\n>| NAIDiffusion -> Hydrus |<\n\n0 - Make Sidecar Files\n1 - Import Directly via API\n2 - Change Config\n\nA: ").lower()
    confdata = config.read()
    if config.readable() and confdata != "" and regularImport != "2":
        print('Config Found')
        configData = json.loads(confdata)
        print(configData)
        importPath = configData["importPath"]
        client = hydrus_api.Client(configData["accessKey"])
        servicekey = configData["serviceKey"]
    elif regularImport == "2":
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey}))
        mainMenu()
    elif (regularImport == "1" or regularImport == "0") and confdata == "":
        print('No Config Found')
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey}))
    print(importPath,client.access_key,servicekey)
mainMenu()
if importPath == "" or client == None or servicekey == "":
    mainMenu(True)
allFiles = os.listdir(importPath)
et = exiftool.ExifToolHelper()
def importFiles():
    for file in allFiles:
        try:
            if file.endswith(".png"):
                #i hate python (and learning it)
                global currentTagList
                global importingFiles
                global regularImport
                global importPath
                global client
                global servicekey
                finalTagList = []
                metadata = et.get_metadata(f"{importPath}\\{file}")
                print('Exporting '+file)
                if metadata[0] != None and metadata[0].get('PNG:Comment') != None:
                    mainData:dict = json.loads(metadata[0]['PNG:Comment'])
                    for key in mainData:
                        if key != "prompt" and key != "uc" and key != "signed_hash":
                            finalTagList.append(f"{key}: {mainData[key]}")
                    tag:str
                    if mainData.get("prompt") != None:
                        for tag in (mainData["prompt"]).split(","):
                            tag = tag.replace('{','').replace('}','').replace('[','').replace(']','').strip()
                            finalTagList.append(f"{tag}")
                if regularImport == "0":
                    f = open(f"{importPath}\\{file}.json", "w")
                    json.dump(finalTagList,f)
                    f.close()
                    continue
                comparingTagList = finalTagList
                lookingfor = ""
                for tagFound in comparingTagList:
                    if tagFound.find("seed:") != -1:
                        print('Found Tag -> '+tagFound)
                        lookingfor = tagFound
                if lookingfor != "":
                    comparingTagList.remove(lookingfor)
                if currentTagList != comparingTagList and currentTagList != []:
                    print('Tag List Changed')
                    res = hydrus_api.utils.add_and_tag_files(client, importingFiles, currentTagList, ['6c6f63616c2074616773'])
                    if res and res[0] and res[0]['status'] and (res[0]['status'] == 2 or res[0]['status'] == 1):
                        print('Successful Import')
                        for filex in importingFiles:
                            os.remove(f"{filex}")
                            print('Deleted Imported File -> '+file)
                    else:
                        print('Failed Import!')
                    importingFiles = []
                currentTagList = comparingTagList
                importingFiles.append(f"{importPath}\\{file}")
                if allFiles.index(file) == len(allFiles)-1:
                    print('Last File')
                    res = hydrus_api.utils.add_and_tag_files(client, importingFiles, currentTagList, ['6c6f63616c2074616773'])
                    if res and res[0] and res[0]['status'] and (res[0]['status'] == 2 or res[0]['status'] == 1):
                        print('Successful Import')
                        for filex in importingFiles:
                            os.remove(f"{filex}")
                            print('Deleted Imported File -> '+file)
                    else:
                        print('Failed Import!')
        except:
            print('Failed to import '+file)
            continue
config.close()
if regularImport == "0":
    if input('!WARNING!\nThis will create a sidecar file for every image in the directory, and insert it into the directory so that you can import it manually into Hydrus. (recommended for large imports) Are you sure you want to continue?\n(y/n)\n').lower() != "y":
        print('Exiting...')
        exit()
elif regularImport == "1":
    if input('!WARNING!\nThis will import every image in the directory and delete the file afterwards to avoid clutter (recommended for one time imports). Are you sure you want to continue?\n(y/n)\n').lower() != "y":
        print('Exiting...')
        exit()
elif regularImport == "2":
    print('Config Saved')
    exit()
importFiles()
        
print('Done!')
exit()