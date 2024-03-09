import os
import json
import exiftool
import hydrus_api
import hydrus_api.utils
import requests
regularImport = ""
importingFiles = []
currentTagList = []
importPath = ""
client = None;
servicekey = ""
config = None
latestCommit = requests.get('https://api.github.com/repos/AlexIsAway/NAITrinkets/commits/main').json()
# print('Latest Commit: '+latestCommit['sha'])
# print('Commit Name: '+latestCommit['commit']['message'])
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
    confdata = ""
    configData:dict = {}
    if config.readable():
        confdata = config.read()
    if confdata != "":
        configData = json.loads(confdata)
    if configData.get('latestCommit') != None and latestCommit['sha'] != configData['latestCommit'] and latestCommit['sha'] != None and latestCommit['sha'] != "" and latestCommit['commit']['message'].find('NAID->Hydrus') != -1:
        print('New Update Available! -> '+latestCommit['commit']['description'])
        print('Download at:\nhttps://github.com/AlexIsAway/NAITrinkets/tree/main/Hydrus/NAID%20to%20Hydrus\n\n')
    if inp == None:
        global regularImport
        regularImport = input("\n>| NAIDiffusion -> Hydrus |<\n\n0 - Make Sidecar Files\n1 - Import Directly via API\n2 - Change Config\n\nA: ").lower()
    config.seek(0)
    if config.readable() and confdata != "" and regularImport != "2":
        print('Config Found')
        print(configData)
        importPath = configData["importPath"]
        client = hydrus_api.Client(configData["accessKey"])
        servicekey = configData["serviceKey"]
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']}))
    elif regularImport == "2":
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print('Invalid Path')
            mainMenu('')
            return
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']}))
        mainMenu()
        return
    elif (regularImport == "1") and confdata == "":
        print('No Config Found')
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print('Invalid Path')
            mainMenu('')
            return
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']})) 
    elif regularImport == "0" and confdata == "":
        print('No Config Found')
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print('Invalid Path')
            mainMenu('')
            return
        config.write(json.dumps({"importPath": importPath, "accessKey": "", "serviceKey": "", "latestCommit": latestCommit['sha']}))
    print(importPath,client.access_key,servicekey)
mainMenu()
if importPath == "":
    mainMenu(True)
allFiles = os.listdir(importPath)
et = exiftool.ExifToolHelper()
# def sortFunc(str):
#     return str.lower()
#allFiles.sort(key=sortFunc)
def importFiles(files):
    #print(files)
    sortList = []
    global currentTagList
    global importingFiles
    currentTagList = []
    importingFiles = []
    for file in files:
        try:
            if file.endswith(".png"):
                #i hate python (and learning it)
                global regularImport
                global importPath
                global client
                global servicekey
                finalTagList = []
                #print(f"{importPath}\\{file}")
                metadata = et.get_metadata(f"{importPath}\\{file}")
                #print('Exporting '+file)
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
                        #print('Found Tag -> '+tagFound)
                        lookingfor = tagFound
                if lookingfor != "":
                    comparingTagList.remove(lookingfor)
                if currentTagList == [] and comparingTagList != []:
                    currentTagList = comparingTagList
                if currentTagList != comparingTagList and currentTagList != []:
                    #print('Tag List Changed\nCurrent:\n\n'+currentTagList.__str__()+"\n\nDifference:\n\n"+comparingTagList.__str__())
                    sortList.append(f"{file}")
                elif currentTagList == comparingTagList:
                    importingFiles.append(f"{importPath}\\{file}")
                if files.index(file) == len(files)-1 and importingFiles != [] and currentTagList != []:
                    print('Last File')
                    res = hydrus_api.utils.add_and_tag_files(client, importingFiles, currentTagList, ['6c6f63616c2074616773'])
                    if res and res[0] and res[0]['status'] and (res[0]['status'] == 2 or res[0]['status'] == 1):
                        print('Successful Import')
                        for filex in importingFiles:
                            os.remove(f"{filex}")
                            print('Deleted Imported File -> '+filex)
                    else:
                        print('Failed Import!')
        except:
            print('Failed to import '+file)
            continue
    if sortList != []:
        importFiles(sortList)
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
importFiles(allFiles)
        
print('Done!')
exit()