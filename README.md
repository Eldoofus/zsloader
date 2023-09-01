# ZSLoader

An experimental modloader for JSON mods for the game ZERO Sievert

## Installation Instructions

Simply place in your ZERO Sievert folder and run!

```
Expected Folder Structure:
ZERO Sievert
|   ZERO Sievert.exe
|   zsloader.py or zsloader.exe
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
```

## Features:

* Enable/Disable mods
* Change mod priority
* Detects and lists all mod conflicts at the level of individual items/list entries
* Special handling for chests and traders (soon)
* Allows manual conflict management (soon)
* Can automatically merge conflicts
* Automatically restores vanilla game files after closing the game
* Python Modding API (soon)

## Mod maker guide

### `gamedata_order.json`

```json
{
    "data" : [
        "gamedata/ammo.json",
        "gamedata/armor.json"
    ],
    "metadata" : {
        "author" : "Eldoofus",
        "name" : "ZSLoader Example Mod",
        "id" : "examplemod"
    },
    "usage" : "index",
    "version" : 1.0
}
```

`data`: List of paths to relevant JSON files.
`metadata`:
* `author`: Mod author
* `name`: Display Name
* `id`: Internal Identifier

`usage`: `"index"`\
`version`: Version number (`X.YZ`)

## User Guide

Simply run the python file or the exe depending on which you downloaded in the commandline