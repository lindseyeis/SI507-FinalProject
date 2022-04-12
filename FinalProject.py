import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://survivor.fandom.com'
CONTESTANT_URL = '/wiki/Category:Survivor_(U.S.)_Contestants'
ALLIANCE_URL = '/wiki/Category:Alliances'

contestant_url = requests.get(BASE_URL + CONTESTANT_URL)
alliance_url = requests.get(BASE_URL + ALLIANCE_URL)

contestant_and_alliance_graph = {} # {'Evie': {'Seasons': ['Survivor 41', 'Survivor 75'], 'Alliances': ['Yase', 'Cool Allaince', ...], 'Bio': 'I am Evie', ... }
contestant_to_url = {} # {'Evie': 'http://survivor.wikia.com/Evie' } We have this so the dropdown knows what url to go to
wiki_html_cache = {} # {'http://survivor.wikia.com/Evie': 'BEAUTIFUL SOUP STUFF'}

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
                alliance_list.append(alliance['href'])

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

for contestant_html in contestants:
    href = contestant_html['href']
    link = BASE_URL + href
    contestant_or_alliance_soup = get_wiki_page(link)
    graph_entry = scrape_contestant_wiki_page(contestant_or_alliance_soup)
    load_contestant_information_to_graph(graph_entry)

for alliance_html in alliances:
    href = alliance_html['href']
    link = BASE_URL + href
    contestant_or_alliance_soup = get_wiki_page(link)
    graph_entry = scrape_alliance_wiki_page(contestant_or_alliance_soup)
    load_alliance_information_to_graph(graph_entry)

# aaron_meredith_info = get_wiki_page('https://survivor.fandom.com/wiki/Aaron_Meredith')
# aaron_meredith_graph_entry = scrape_contestant_wiki_page(aaron_meredith_info)
# load_information_to_graph(aaron_meredith_graph_entry)
print(contestant_and_alliance_graph)