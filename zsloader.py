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

import rapidjson
import os
import subprocess
import shutil
import copy

vanilla = open("./ZS_vanilla/gamedata_order.json").read()
dump = open('dump.json', 'w')

print("Backing Up Vanilla Data...")
shutil.copytree("./ZS_vanilla", "./ZS_backup")

modlist = []
enabled = []
folders = []

try:
    print("Loading Vanilla Data...")
    vanilla = rapidjson.loads(vanilla)['data']
    data = {}
    for i in vanilla:
        try:
            data[i[9:-5]] = rapidjson.loads(open("ZS_vanilla/" + i).read(), parse_mode = rapidjson.PM_TRAILING_COMMAS)
            print("  Loaded " + i)
        except:
            print("  Error loading " + i)
            exit()

    print("Finding Mods...")
    mods = os.listdir("./ZS_mods")
    for i in mods:
        if os.path.isdir("./ZS_mods/" + i):
            print("  ", end='')
            if os.path.exists("./ZS_mods/" + i + "/gamedata_order.json"):
                try:
                    modlist.append(rapidjson.loads(open("./ZS_mods/" + i + "/gamedata_order.json").read(), parse_mode = rapidjson.PM_TRAILING_COMMAS))
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
            elif os.path.exists("./ZS_mods/" + i + "/gamedata_order.rapidjson.disabled"):
                try:
                    modlist.append(rapidjson.loads(open("./ZS_mods/" + i + "/gamedata_order.rapidjson.disabled").read(), parse_mode = rapidjson.PM_TRAILING_COMMAS))
                    enabled.append(False)
                    folders.append(i)
                    if 'metadata' in modlist[-1] and 'id' in modlist[-1]['metadata']:
                        print('Found ' + modlist[-1]['metadata']['id'] + ' in folder ' + i)
                    else:
                        modlist.pop()
                        enabled.pop()
                        folders.pop()
                        raise Exception("Error reading " + i + "/gamedata_order.rapidjson.disabled")
                except:
                    print("Error reading " + i)

    print("Loading Config...")
    if os.path.exists("./zsloader.config"):
        config = rapidjson.loads(open("./zsloader.config").read())
    else:
        config = {}

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
                    moddata[modlist[i]['metadata']['id']][j[9:-5]] = rapidjson.loads(open("./ZS_mods/" + modlist[i]['metadata']['id'] + "/" + j).read())
                    print("  Loaded " + j + " from " + modlist[i]['metadata']['id'])
                except:
                    print("  Error loading " + j + " from " + modlist[i]['metadata']['id'])

    def diff(a, b):
        if a == b:
            return {}
        if type(a) == dict and type(b) == dict:
            added = {}
            for i in b:
                if i not in a:
                    added[i] = b[i]
            removed = {}
            for i in a:
                if i not in b:
                    removed[i] = a[i]
            changed = {}
            for i in a:
                if i in b:
                    c = diff(a[i], b[i])
                    if c != {}:
                        changed[i] = c
            result = {}
            if added != {}:
                result['added'] = added
            if removed != {}:
                result['removed'] = removed
            if changed != {}:
                result['changed'] = changed
            return result
        elif type(a) == list and type(b) == list:
            #order doesnt matter
            added = []
            removed = []
            changed = {}
            for i in range(len(a)):
                if type(a[i]) == dict:
                    t = 'item'
                    if 'id' in a[i]:
                        t = 'id'
                    f = False
                    for j in range(len(b)):
                        if type(b[j]) == dict and t in b[j] and a[i][t] == b[j][t]:
                            f = True
                            d = diff(a[i], b[j])
                            if d != {}:
                                changed[i] = d
                                break
                    if not f:
                        removed.append(a[i])
                elif a[i] not in b:
                    removed.append(a[i])
            for i in range(len(b)):
                if type(b[i]) == dict:
                    t = 'item'
                    if 'id' in b[i]:
                        t = 'id'
                    f = False
                    for j in range(len(a)):
                        if type(a[j]) == dict and t in a[j] and b[i][t] == a[j][t]:
                            f = True
                            break
                    if not f:
                        added.append(b[i])
                elif b[i] not in a:
                    added.append(b[i])
            result = {}
            if added != []:
                result['added'] = added
            if removed != []:
                result['removed'] = removed
            if changed != {}:
                result['changed'] = changed
            return result
        else:
            return b

    def apply(a, d):
        if type(a) == dict and type(d) == dict:
            b = copy.deepcopy(a)
            if 'added' in d:
                for i in d['added']:
                    b[i] = copy.deepcopy(d['added'][i])
            if 'removed' in d:
                for i in d['removed']:
                    del b[i]
            if 'changed' in d:
                for i in d['changed']:
                    b[i] = apply(a[i], d['changed'][i])
            return b

        elif type(a) == list and type(d) == dict:
            c = []
            if 'changed' in d:
                for i in d['changed']:
                    c.append(apply(a[i], d['changed'][i]))
            else:
                c = copy.deepcopy(a)
            r = []
            if 'removed' in d:
                for i in range(len(c)):
                    if i not in d['removed']:
                        r.append(copy.deepcopy(c[i]))
            else:
                r = copy.deepcopy(c)
            if 'added' in d:
                for i in d['added']:
                    r.append(copy.deepcopy(i))
            return r
        else:
            return copy.deepcopy(d)

    print("Generating Diffs...")
    diffs = {}
    for j in data:
        diffs[j] = {'added' : {}, 'removed' : {}, 'changed' : {}}
        for i in range(len(modlist)):
            if enabled[i] and j in moddata[modlist[i]['metadata']['id']]:
                if j not in data:
                    data[j] = { 'data' : {} }
                print("  Generating diffs for " + j + " from " + modlist[i]['metadata']['id'])
                d = diff(data[j]['data'], moddata[modlist[i]['metadata']['id']][j]['data'])
                if 'added' in d:
                    for k in d['added']:
                        if k not in diffs[j]['added']:
                            diffs[j]['added'][k] = []
                        diffs[j]['added'][k].append({ 'mod' : modlist[i]['metadata']['id'], 'diff' : d['added'][k]})
                        print("    Added " + k)
                if 'removed' in d:
                    for k in d['removed']:
                        if k not in diffs[j]['removed']:
                            diffs[j]['removed'][k] = []
                        diffs[j]['removed'][k].append({ 'mod' : modlist[i]['metadata']['id'], 'diff' : d['removed'][k]})
                        print("    Removed " + k)
                if 'changed' in d:
                    for k in d['changed']:
                        if k not in diffs[j]['changed']:
                            diffs[j]['changed'][k] = []
                        diffs[j]['changed'][k].append({ 'mod' : modlist[i]['metadata']['id'], 'diff' : d['changed'][k]})
                        print("    Changed " + k)              

    print("Detecting Conflicts...")
    conflicts = {}
    for j in diffs:
        conflicts[j] = {}
        for k in diffs[j]['changed']:
            if len(diffs[j]['changed'][k]) > 1:
                conflicts[j][k] = []
                for l in diffs[j]['changed'][k]:
                    conflicts[j][k].append(l['mod'])
            if k in diffs[j]['removed']:
                if k not in conflicts:
                    conflicts[j][k] = [diffs[j]['removed'][k][0]['mod']]
                for l in diffs[j]['removed'][k]:
                    conflicts[j][k].append(l['mod'])
            
    print(rapidjson.dumps(conflicts, indent=4))

    print("Select an option:")
    print("  1. Resolve Conflicts Automatically")
    print("  2. Resolve Conflicts Manually")
    print("  3. Resolve Conflicts from Config")
    print("  4. Abort")

    while True:
        i = input("Select an option: ")
        if i == '1':
            print("Resolving Conflicts Automatically...")
            break
        elif i == '2':
            print("Resolving Conflicts Manually...")
            print("Still Under Construction")
            break
        elif i == '3':
            print("Resolving Conflicts from Config...")
            print("Still Under Construction")
            break
        elif i == '4':
            print("Aborting...")
            exit()
        else:
            print("Invalid Input")

    print("Merging Data...")
    for j in diffs:
        for k in diffs[j]['added']:
            data[j]['data'][k] = apply({}, diffs[j]['added'][k][0]['diff'])
        for k in diffs[j]['removed']:
            del data[j]['data'][k]
        for k in diffs[j]['changed']:
            data[j]['data'][k] = apply(data[j]['data'][k], diffs[j]['changed'][k][0]['diff'])
            print("  Merged " + k + " from " + diffs[j]['changed'][k][0]['mod'])

    print("Writing Data...")
    for i in data:
        open("./ZS_vanilla/gamedata/" + i + ".json", "w").write(rapidjson.dumps(data[i], indent=4))
        print("Wrote " + i)

    print("Launching Game...")
    subprocess.run(["./ZERO Sievert.exe"])
    print("Game Closed")
finally:
    print("Saving Config...")
    for i in range(len(modlist)):
        if enabled[i] and os.path.exists("./ZS_mods/" + folders[i] + "/gamedata_order.rapidjson.disabled"):
            os.rename("./ZS_mods/" + folders[i] + "/gamedata_order.rapidjson.disabled", "./ZS_mods/" + folders[i] + "/gamedata_order.json")
        elif not enabled[i] and os.path.exists("./ZS_mods/" + folders[i] + "/gamedata_order.json"):
            os.rename("./ZS_mods/" + folders[i] + "/gamedata_order.json", "./ZS_mods/" + folders[i] + "/gamedata_order.rapidjson.disabled")
    config['mod_order'] = []
    for i in modlist:
        config['mod_order'].append(i['metadata']['id'])
    open("./zsloader.config", "w").write(rapidjson.dumps(config, indent=4))
    print("Restoring Vanilla...")
    shutil.rmtree("./ZS_vanilla")
    shutil.copytree("./ZS_backup", "./ZS_vanilla")
    print("Done")
    print("Cleaning Up...")
    shutil.rmtree("./ZS_backup")
    dump.close()
    print("Done")