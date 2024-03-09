import os
import json
import exiftool
import hydrus_api
import hydrus_api.utils
import requests
hasColored = False
Style = None
Fore = None
Back = None
try:
    from colored import Style, Fore, Back, set_tty_aware
    hasColored = True
except ImportError:
    print('No Colored Package')
###
# yoinked from stackoverflow
###
from sys import stdin, stdout
from platform import system
if system() == "Windows":
    from msvcrt import getch, kbhit
else:
    from termios import TCSADRAIN, tcgetattr, tcsetattr
    from select import select
    from tty import setraw
    from sys import stdin
    def getch() -> bytes:
        fd = stdin.fileno()
        old_settings = tcgetattr(fd)
        try:
            setraw(fd)
            return stdin.read(1).encode()
        finally:
            tcsetattr(fd, TCSADRAIN, old_settings)
    def kbhit() -> bool:
        return bool(select([stdin], [], [], 0)[0])
def isansitty() -> bool:
    while kbhit():
        getch()
    stdout.write("\x1b[6n")
    stdout.flush()
    stdin.flush()
    if kbhit():
        if ord(getch()) == 27 and kbhit():
            if getch() == b"[":
                while kbhit():
                    getch()

                return stdout.isatty()
    stdout.write('\b\b\b\b')
    return False
if not isansitty():
    hasColored = False
if not hasColored:
    # Mimic colored package with empty values
    class Style:
        reset = ''
        underline = ''
    class Fore:
        red = ''
        green = ''
        blue = ''
        magenta = ''
        light_yellow = ''
    class Back:
        red = ''
        dark_red_1 = ''
        black = ''
    # only mimic used values
###
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
        nud = latestCommit['commit']
        if nud.get('description') != None:
            nud = nud['description']
        else:
            nud = nud['message']
        print(f'\n{Fore.red}New Update Available!{Style.reset} -> {nud}')
        print(f'\nDownload at:\n{Fore.blue}{Style.underline}https://github.com/AlexIsAway/NAITrinkets/tree/main/Hydrus/NAID%20to%20Hydrus{Style.reset}')
    if inp == None:
        global regularImport
        regularImport = input(f"\n{Fore.blue}>| NAIDiffusion -> Hydrus |<{Style.reset}\n\n0 - Make Sidecar Files\n1 - Import Directly via API\n2 - Change Config\n\nA: ").lower()
    config.seek(0)
    if config.readable() and confdata != "" and regularImport != "2":
        print(f'{Fore.green}Config Found{Style.reset}')
        #print(configData)
        importPath = configData["importPath"]
        client = hydrus_api.Client(configData["accessKey"])
        servicekey = configData["serviceKey"]
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']}))
    elif regularImport == "2":
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print(f'{Fore.red}Invalid Path{Style.reset}')
            mainMenu('')
            return
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']}))
        mainMenu()
        return
    elif (regularImport == "1") and confdata == "":
        print(f'{Fore.yellow}No Config Found{Style.reset}')
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print(f'{Fore.red}Invalid Path{Style.reset}')
            mainMenu('')
            return
        client = hydrus_api.Client(input("Enter your access key:\n"))
        servicekey = input("Enter a file domain service key:\n")
        config.write(json.dumps({"importPath": importPath, "accessKey": client.access_key, "serviceKey": servicekey, "latestCommit": latestCommit['sha']})) 
    elif regularImport == "0" and confdata == "":
        print(f'{Fore.yellow}No Config Found{Style.reset}')
        importPath = input("Enter the path to the directory you want to import (entire absolute path):\n")
        if os.path.exists(importPath) == False:
            print(f'{Fore.red}Invalid Path{Style.reset}')
            mainMenu('')
            return
        config.write(json.dumps({"importPath": importPath, "accessKey": "", "serviceKey": "", "latestCommit": latestCommit['sha']}))
    #print(importPath,client.access_key,servicekey)
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
                        print(f'{Fore.green}Successful Import{Style.reset}')
                        for filex in importingFiles:
                            os.remove(f"{filex}")
                            print('Deleted Imported File -> '+filex)
                    else:
                        print(f'{Fore.red}Failed Import!{Style.reset}')
        except:
            print(f'{Fore.red}Failed to import{Style.reset} '+file)
            continue
    if sortList != []:
        importFiles(sortList)
config.close()
if regularImport == "0":
    if input(f'{Fore.light_yellow}!WARNING!\n{Back.red}This will create a sidecar file for every image in the directory, and insert it into the directory so that you can import it manually into Hydrus.\n{Style.reset}Are you sure you want to continue? (y/n)\n').lower() != "y":
        print('Exiting...')
        exit()
elif regularImport == "1":
    if input(f'{Back.dark_red_1}{Fore.light_yellow}!WARNING!{Back.black}\n{Fore.red}This will import every image in the directory and delete the file afterwards!\n{Style.reset}Are you sure you want to continue? (y/n)\n').lower() != "y":
        print('Exiting...')
        exit()
elif regularImport == "2":
    print(f'{Fore.green}Config Saved{Style.reset}')
    exit()
importFiles(allFiles)
        
print(f'{Fore.magenta}Done!{Style.reset}')
exit()