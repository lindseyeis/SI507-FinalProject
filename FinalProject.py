import pymongo
import certifi

contestant_and_alliance_graph = {} # {'Evie': {'Seasons': ['Survivor 41', 'Survivor 75'], 'Alliances': ['Yase', 'Cool Allaince', ...], 'Bio': 'I am Evie', ... }
contestant_to_url = {} # {'Evie': 'http://survivor.wikia.com/Evie' } We have this so the dropdown knows what url to go to
wiki_html_cache = {} # {'http://survivor.wikia.com/Evie': 'BEAUTIFUL SOUP STUFF'}
contestants_list = []
alliances_list = []

client = pymongo.MongoClient("mongodb+srv://lindseyeis:fairviews@cluster0.pevav.mongodb.net/507FinalProject", tlsCAFile=certifi.where())
db = client['507FinalProject']
collection = db['507FinalProject']

def get_contestant_or_alliance(contestant_or_alliance_name):
    if contestant_or_alliance_name in contestant_and_alliance_graph:
        return contestant_and_alliance_graph[contestant_or_alliance_name]
    else:
        found_entry = collection.find_one({"Name": contestant_or_alliance_name})
        return found_entry

def get_all_contestants_and_alliances_mongo():
    entries = collection.find({})
    for entry in entries:
        if "Members" in entry:
            contestant_and_alliance_graph[entry["Name"]] = entry["Members"]
            alliances_list.append(entry["Name"])
        elif "Seasons" in entry:
            graph_entry = {}
            for key in entry:
                if key != "Name":
                    graph_entry.update({key: entry[key]})
            contestant_and_alliance_graph[entry["Name"]] = graph_entry
            contestants_list.append(entry["Name"])

def mongo_entries():
    for contestant_or_alliance_name in contestant_and_alliance_graph:
        contestant_or_alliance_info = contestant_and_alliance_graph[contestant_or_alliance_name]
        print(contestant_or_alliance_info)
        if contestant_or_alliance_name is not None and contestant_or_alliance_name in contestants_list:
            entry = {"Name": contestant_or_alliance_name}
            entry.update(contestant_or_alliance_info)
            found_entry = collection.find_one({"Name": contestant_or_alliance_name})
            if found_entry is None:
                mongo = collection.insert_one(entry)
            print(found_entry)
        elif contestant_or_alliance_name is not None and contestant_or_alliance_name in alliances_list:
            entry = {"Name": contestant_or_alliance_name, "Members": contestant_or_alliance_info}
            found_entry = collection.find_one({"Name": contestant_or_alliance_name})
            if found_entry is None:
                mongo = collection.insert_one(entry)
            print(found_entry)


# Breadth-first search all contestants and alliances
def get_path_to_victory(contestant_or_alliance_entry):
    print('Calculating shortest path. This may take several minutes.')
    print(contestant_and_alliance_graph)
    queue = []
    visited_nodes = []

    queue.append([contestant_or_alliance_entry])

    while len(queue) > 0:
        pathToInspect = queue.pop(0)
        nameToInspect = pathToInspect[-1]
        print('Inspecting node ' + nameToInspect)
        if nameToInspect in contestants_list or nameToInspect in alliances_list:
            nodeToInspect = contestant_and_alliance_graph[nameToInspect]
            print(nodeToInspect)
        else:
            print('Error: Failed to find contestant or alliance. Continuing...')
            continue
        if nameToInspect in contestants_list:
            contestant_seasons = nodeToInspect['Seasons']
            isWinner = False
            for season in contestant_seasons:
                if contestant_seasons[season] == "Winner":
                    isWinner = True
            if isWinner:
                print('Found the winner ' + nameToInspect)
                print(pathToInspect)
                return pathToInspect
        if nodeToInspect not in visited_nodes:
            if nameToInspect in contestants_list:
                neighborNodes = nodeToInspect['Alliances']
            elif nameToInspect in alliances_list:
                neighborNodes = nodeToInspect
            print(neighborNodes)
            for neighborNode in neighborNodes:
                newPath = pathToInspect.copy()
                newPath.append(neighborNode)
                queue.append(newPath)
        visited_nodes.append(nodeToInspect)
    return ["This contestant has no path to victory :("]