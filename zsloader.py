'''
ZSLoader for ZERO Sievert JSON Mods
By Eldoofus

Expected Folder Structure:
ZERO Sievert
|   ZERO Sievert.exe
|   zsloader.py
|   ZS_vanilla
|   |   gamedata_order.json
|   |   gamedata
|   |   |   blahblahblah.json
|   ZS_mods
|   |   mod1
|   |   |   gamedata_order.json
|   |   |   gamedata
|   |   |   |   something.json
|   |   mod2
|   |   |   gamedata_order.json
|   |   |   gamedata
|   |   |   |   something.json
'''

import json
import os
import subprocess
import shutil
import jsonpatch

vanilla = open("./ZS_vanilla/gamedata_order.json").read()
dump = open('dump.json', 'w')

print("Backing Up Vanilla Data...")
shutil.copytree("./ZS_vanilla", "./ZS_backup")

try:
    print("Loading Vanilla Data...")
    vanilla = json.loads(vanilla)['data']
    data = {}
    for i in vanilla:
        data[i[9:-5]] = json.loads(open("ZS_vanilla/" + i).read())
        print("Loaded " + i)

    print("Finding Mods...")
    mods = os.listdir("./ZS_mods")
    modlist = []
    enabled = []
    folders = []
    for i in mods:
        if os.path.isdir("./ZS_mods/" + i):
            if os.path.exists("./ZS_mods/" + i + "/gamedata_order.json"):
                try:
                    modlist.append(json.loads(open("./ZS_mods/" + i + "/gamedata_order.json").read()))
                    enabled.append(True)
                    folders.append(i)
                    if 'metadata' in modlist[-1] and 'id' in modlist[-1]['metadata']:
                        print('Found ' + modlist[-1]['metadata']['id'] + ' in folder ' + i)
                    else:
                        modlist.pop()
                        enabled.pop()
                        folders.pop()
                        raise Exception("Error reading " + i + "/gamedata_order.json")
                except:
                    print("Error reading " + i)
            elif os.path.exists("./ZS_mods/" + i + "/gamedata_order.json.disabled"):
                try:
                    modlist.append(json.loads(open("./ZS_mods/" + i + "/gamedata_order.json.disabled").read()))
                    enabled.append(False)
                    folders.append(i)
                    if 'metadata' in modlist[-1] and 'id' in modlist[-1]['metadata']:
                        print('Found ' + modlist[-1]['metadata']['id'] + ' in folder ' + i)
                    else:
                        modlist.pop()
                        enabled.pop()
                        folders.pop()
                        raise Exception("Error reading " + i + "/gamedata_order.json.disabled")
                except:
                    print("Error reading " + i)

    print("Loading Config...")
    if os.path.exists("./zsloader.config"):
        config = json.loads(open("./zsloader.config").read())
        print('beans')
    else:
        config = {}

    #reorder mods based on config
    if 'mod_order' in config:
        for i in range(len(config['mod_order'])-1, -1, -1):
            if config['mod_order'][i] in [m['metadata']['id'] for m in modlist]:
                j = [m['metadata']['id'] for m in modlist].index(config['mod_order'][i])
                modlist.insert(0, modlist.pop(j))
                enabled.insert(0, enabled.pop(j))
                folders.insert(0, folders.pop(j))
            
    
    while True:
        print()
        print('ZSLoader by Eldoofus:')
        print('  1. Enable/Disable Mods')
        print('  2. Change Mod Load Order')
        print('  3. Launch Game')
        print('  4. Exit')
        print()
        i = input('Select an option: ')
        if i == '1':
            while True:
                print()
                print('Mod List: ')
                for i in range(len(modlist)):
                    if 'name' in modlist[i]['metadata']:
                        print(' ' + (str(i+1) + '.').ljust(len(str(len(modlist))) + 2) + modlist[i]['metadata']['name'] + (' (disabled)' if not enabled[i] else ''))
                    else:
                        print(' ' + (str(i+1) + '.').ljust(len(str(len(modlist))) + 2) + modlist[i]['metadata']['id'] + (' (disabled)' if not enabled[i] else ''))
                print()
                i = input('Select a mod to enable/disable (0 to exit): ')
                if i == '0':
                    break
                elif i.isdigit() and int(i) > 0 and int(i) <= len(modlist):
                    enabled[int(i)-1] = not enabled[int(i)-1]
                else:
                    print('Invalid Input')
        elif i == '2':
            while True:
                print()
                print('Mod List: ')
                for i in range(len(modlist)):
                    if 'name' in modlist[i]['metadata']:
                        print(' ' + (str(i+1) + '.').ljust(len(str(len(modlist))) + 2) + modlist[i]['metadata']['name'] + (' (disabled)' if not enabled[i] else ''))
                    else:
                        print(' ' + (str(i+1) + '.').ljust(len(str(len(modlist))) + 2) + modlist[i]['metadata']['id'] + (' (disabled)' if not enabled[i] else ''))
                print()
                i = input('Select a mod to move (0 to exit): ')
                if i == '0':
                    break
                elif i.isdigit() and int(i) > 0 and int(i) <= len(modlist):
                    j = input('Move ' + modlist[int(i)-1]['metadata']['id'] + ' to position: ')
                    if j.isdigit() and int(j) > 0 and int(j) <= len(modlist):
                        modlist.insert(int(j)-1, modlist.pop(int(i)-1))
                        enabled.insert(int(j)-1, enabled.pop(int(i)-1))
                        folders.insert(int(j)-1, folders.pop(int(i)-1))
                    else:
                        print('Invalid Input')
                else:
                    print('Invalid Input')
        elif i == '3':
            break
        elif i == '4':
            exit()
        else:
            print('Invalid Input')

    print("Loading Mod Data...")
    moddata = {}
    for i in range(len(modlist)):
        if enabled[i]:
            moddata[modlist[i]['metadata']['id']] = {}
            for j in modlist[i]['data']:
                try:
                    moddata[modlist[i]['metadata']['id']][j[9:-5]] = json.loads(open("./ZS_mods/" + modlist[i]['metadata']['id'] + "/" + j).read())
                    print("Loaded " + j + " from " + modlist[i]['metadata']['id'])
                except:
                    print("Error loading " + j + " from " + modlist[i]['metadata']['id'])

    print("Generating Diffs...")
    diffs = {}
    for mod in moddata:
        diffs[mod] = {}
        for i in moddata[mod]:
            if i not in data:
                data[i] = {}
            diffs[mod][i] = jsonpatch.JsonPatch.from_diff(data[i], moddata[mod][i])

    #dump diffs
    for mod in diffs:
        dump.write("\n\n" + mod + "\n")
        for diff in diffs[mod]:
            dump.write("\n" + diff + "\n")
            dump.write(json.dumps(diffs[mod][diff].patch, indent=4))

    print("Merging Data...")
    #merge data with diffs from lowest to highest priority
    for mod in reversed([m['metadata']['id'] for m in modlist]):
        for i in diffs[mod]:
            print("Merging " + i + " from " + mod)
            data[i] = diffs[mod][i].apply(data[i])

    print("Writing Data...")
    for i in data:
        open("./ZS_vanilla/gamedata/" + i + ".json", "w").write(json.dumps(data[i], indent=4))
        print("Wrote " + i)

    print("Launching Game...")
    subprocess.run(["./ZERO Sievert.exe"])
    print("Game Closed")

    print("Restoring Vanilla...")
    shutil.rmtree("./ZS_vanilla")
    shutil.copytree("./ZS_backup", "./ZS_vanilla")
    print("Done")
finally:
    print("Saving Config...")
    for i in range(len(modlist)):
        if enabled[i] and os.path.exists("./ZS_mods/" + folders[i] + "/gamedata_order.json.disabled"):
            os.rename("./ZS_mods/" + folders[i] + "/gamedata_order.json.disabled", "./ZS_mods/" + folders[i] + "/gamedata_order.json")
        elif not enabled[i] and os.path.exists("./ZS_mods/" + folders[i] + "/gamedata_order.json"):
            os.rename("./ZS_mods/" + folders[i] + "/gamedata_order.json", "./ZS_mods/" + folders[i] + "/gamedata_order.json.disabled")
    config['mod_order'] = []
    for i in modlist:
        config['mod_order'].append(i['metadata']['id'])
    open("./zsloader.config", "w").write(json.dumps(config, indent=4))
    print("Cleaning Up...")
    shutil.rmtree("./ZS_backup")
    dump.close()
    print("Done")