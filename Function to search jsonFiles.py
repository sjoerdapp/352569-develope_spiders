import json

json_string = """

        {
            "content": "test0",
            "test": {
                "content": "test1"
            },
            "test2": {
                "content": "test2",
                "asdf": {
                    "content": "test3"
                }
            }
        } 

"""

myDict = json.loads(json_string)

myDict                


def getByKeyName(inputVariable, searchKey):
    foundItems = []

    if isinstance(inputVariable, dict):
        for currentKey, currentVar in inputVariable.items():
            if currentKey == searchKey:
                foundItems = foundItems + [currentVar]
            else:
                foundItems = foundItems + getByKeyName(currentVar, searchKey)
    if isinstance(inputVariable, list):
        for currentVar in inputVariable:
            foundItems = foundItems + getByKeyName(currentVar, searchKey)
    
    return foundItems

getByKeyName(myDict, "content")
