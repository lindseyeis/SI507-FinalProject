import requests
from bs4 import BeautifulSoup
import pymongo
import dns
import ssl
import certifi

BASE_URL = 'https://survivor.fandom.com'
CONTESTANT_URL = '/wiki/Category:Survivor_(U.S.)_Contestants'
ALLIANCE_URL = '/wiki/Category:Alliances'

contestant_and_alliance_graph = {} # {'Evie': {'Seasons': ['Survivor 41', 'Survivor 75'], 'Alliances': ['Yase', 'Cool Allaince', ...], 'Bio': 'I am Evie', ... }
contestant_to_url = {} # {'Evie': 'http://survivor.wikia.com/Evie' } We have this so the dropdown knows what url to go to
wiki_html_cache = {} # {'http://survivor.wikia.com/Evie': 'BEAUTIFUL SOUP STUFF'}
contestants_list = []
alliances_list = []

client = pymongo.MongoClient("mongodb+srv://lindseyeis:fairviews@cluster0.pevav.mongodb.net/507FinalProject", tlsCAFile=certifi.where())
db = client['507FinalProject']
collection = db['507FinalProject']

# This function returns the beautiful soup for a contestant or alliance
def get_wiki_page(contestant_or_alliance_url):
    # {'Evie': 'beautiful soup info here'}
    # {'Yase Alliance': 'beautiful soup here'}
    if contestant_or_alliance_url not in wiki_html_cache:
        contestant_link = requests.get(contestant_or_alliance_url)
        contestant_soup = BeautifulSoup(contestant_link.content, 'html.parser')
        wiki_html_cache[contestant_or_alliance_url] = contestant_soup
    return wiki_html_cache[contestant_or_alliance_url]

# Contestant table: contestant name, alliance name, individual ranking
# Alliance table: alliance name, alliance members

# First, look up the contestant Evie in the contestants table
# Now, we have Evie's alliance name, Yase
# We look up Yase in the alliance page
# This gives us all of the other members of that alliance
# Now, we look up all the other members in the contestant table (Xander, Genie, etc.)
# We get their information and use all of this to decide whether it was a winning alliance

# wiki_page_contents will be the beautiful soup
def scrape_contestant_wiki_page(wiki_page_contents):
    title = wiki_page_contents.find("h2", {"data-source": "title"}, recursive=True)
    if title is not None:
        contestant_name = title.text
    else:
        return None

    all_divs = wiki_page_contents.find("div", {"data-source": "alliances"}, recursive=True)
    alliance_list = []
    if all_divs is not None:
        alliances = all_divs.find_all("a", href=True, recursive=True)
        if alliances is not None:
            for alliance in alliances:
                alliance_list.append(alliance['title'])

    all_seasons = wiki_page_contents.find("nav", {"data-item-name": "season"}, recursive=True)
    all_seasons_and_places = {}
    i = 1
    for season in all_seasons:
        if i == 1:
            season_tag = "place"
        else:
            season_tag = "place" + str(i)
        season_place = wiki_page_contents.find("div", {"data-source": season_tag}, recursive=True)
        if season is not None and season_place is not None:
            place = season_place.text
            split_place = place.split("\n")
            all_seasons_and_places[season.text] = split_place[2]
        i += 1

    # {'Name': 'Evie', 'Alliances': ['Yase']}
    # 'Seasons': {'Survivor 41': 14/16, 'Survivor 75': 2/20, ...}
    return {'Name': contestant_name, 'Alliances': alliance_list, 'Seasons': all_seasons_and_places}

def scrape_alliance_wiki_page(wiki_page_contents):
    title = wiki_page_contents.find("h2", {"data-source": "name"}, recursive=True)
    if title is not None:
        alliance_name = title.text
    else:
        return None

    members = wiki_page_contents.find_all("div", {"class": "floatnone"})
    member_names = []
    if members is not None:
        for member in members:
            member_name_html = member.find("a", recursive=True)
            if member_name_html is not None:
                member_names.append(member_name_html["title"])

    return {'Alliance Name': alliance_name, 'Members': member_names}

# contestant_info will be like {"Evie": "Survivor 41", "Yase Alliance",...}
def load_contestant_information_to_graph(contestant_info):
    # Check if contestant is already in the graph
    # If contestant not in graph, add to graph
    if contestant_info is not None:
        contestant_name = contestant_info['Name']
        if contestant_name not in contestant_and_alliance_graph:
            # contestant_graph is expecting to be in the format {'Evie': {'Alliances': ['Yase'], 'Seasons': ['Survivor 41'],...}
            contestant_and_alliance_graph[contestant_name] = {'Alliances': contestant_info['Alliances'], 'Seasons': contestant_info['Seasons']}

def load_alliance_information_to_graph(alliance_info):
    if alliance_info is not None:
        alliance_name = alliance_info['Alliance Name']
        if alliance_name not in contestant_and_alliance_graph:
            # contestant_graph is expecting to be in the format {'Aitu Four': ['Yul', 'Becky', ...]}
            contestant_and_alliance_graph[alliance_name] = alliance_info['Members']

def scrape_all_contestant_and_alliance_pages():
    contestant_url = requests.get(BASE_URL + CONTESTANT_URL)
    alliance_url = requests.get(BASE_URL + ALLIANCE_URL)

    all_contestants_soup = BeautifulSoup(contestant_url.content, 'html.parser')
    alliance_soup = BeautifulSoup(alliance_url.content, 'html.parser')

    contestants = []
    contestants.extend(all_contestants_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True))

    pagination_buttons = all_contestants_soup.find("div", {"class": "category-page__pagination"})
    next_button = pagination_buttons.find("a", {"class": "category-page__pagination-next wds-button wds-is-secondary"})

    # While there's still a next button, we need to go to the next page and get all the contestants from that page
    while next_button is not None:
        # First, get the link to the next page
        next_button_link = next_button['href']
        # Go to the next page url
        contestant_page_url = requests.get(next_button_link)
        # Convert the next page to soup
        all_contestants_soup = BeautifulSoup(contestant_page_url.content, 'html.parser')
        # For each contestant on that page, add those contestants to the contestant list
        contestants.extend(all_contestants_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True))
        # See if there's another next button, and if so, keep going
        pagination_buttons = all_contestants_soup.find("div", {"class": "category-page__pagination"})
        next_button = pagination_buttons.find("a", {"class": "category-page__pagination-next wds-button wds-is-secondary"})

    alliances = alliance_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True)
    for contestant_html in contestants:
        href = contestant_html['href']
        link = BASE_URL + href
        contestant_or_alliance_soup = get_wiki_page(link)
        graph_entry = scrape_contestant_wiki_page(contestant_or_alliance_soup)
        load_contestant_information_to_graph(graph_entry)
        print(contestants_list)
        print(graph_entry)
        if graph_entry is not None and graph_entry['Name'] is not None:
            contestants_list.append(graph_entry['Name'])

    print('Scraping alliances')
    for alliance_html in alliances:
        href = alliance_html['href']
        link = BASE_URL + href
        contestant_or_alliance_soup = get_wiki_page(link)
        graph_entry = scrape_alliance_wiki_page(contestant_or_alliance_soup)
        load_alliance_information_to_graph(graph_entry)
        print('this is the graph entry')
        print(graph_entry)
        if graph_entry is not None and graph_entry['Alliance Name'] is not None:
            alliances_list.append(graph_entry['Alliance Name'])
    print(contestant_and_alliance_graph)

# Gets a contestant or alliance from either the cache or the database.
# Will always try to retrieve from the cache before adding to the database.
def get_contestant_or_alliance(contestant_or_alliance_name):
    # We have already found this contestant or alliance - retrieve it from the graph
    if contestant_or_alliance_name in contestant_and_alliance_graph:
        return contestant_and_alliance_graph[contestant_or_alliance_name]
    else:
        found_entry = collection.find_one({"Name": contestant_or_alliance_name})
        return found_entry
# aaron_meredith_info = get_wiki_page('https://survivor.fandom.com/wiki/Aaron_Meredith')
# aaron_meredith_graph_entry = scrape_contestant_wiki_page(aaron_meredith_info)
# load_information_to_graph(aaron_meredith_graph_entry)

def get_all_contestants_and_alliances_mongo():
    entries = collection.find({})
    for entry in entries:
        # This is for alliances
        if "Members" in entry:
            contestant_and_alliance_graph[entry["Name"]] = entry["Members"]
            alliances_list.append(entry["Name"])
        # This is for contestants
        elif "Seasons" in entry:
            graph_entry = {}
            for key in entry:
                if key != "Name":
                    graph_entry.update({key: entry[key]})
            contestant_and_alliance_graph[entry["Name"]] = graph_entry
            contestants_list.append(entry["Name"])

def mongo_entries():
    for contestant_or_alliance_name in contestant_and_alliance_graph:
        # "Evie": {"Seasons": ["Survivor 41"], ...}
        contestant_or_alliance_info = contestant_and_alliance_graph[contestant_or_alliance_name]
        print(contestant_or_alliance_info)
        # Determine if this is an alliance or contestant
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
        # {"Name": "Evie", "Seasons": ["Survivor 41"], ...}

    print('printed mongo entries')

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
        # If this is a contestant, check if they're the winner
        if nameToInspect in contestants_list:
            contestant_seasons = nodeToInspect['Seasons']
            isWinner = False
            for season in contestant_seasons:
                # {Island of the Idols: 11/20}
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
    print("Sorry, couldn't find a connection")
    return