import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://survivor.fandom.com'

url = requests.get(BASE_URL + '/wiki/Category:Survivor_(U.S.)_Contestants')
contestant_graph = {} # {'Evie': {'Seasons': ['Survivor 41', 'Survivor 75'], 'Alliances': ['Yase', 'Cool Allaince', ...], 'Bio': 'I am Evie', ... }
contestant_to_url = {} # {'Evie': 'http://survivor.wikia.com/Evie' } We have this so the dropdown knows what url to go to
wiki_html_cache = {} # {'http://survivor.wikia.com/Evie': 'BEAUTIFUL SOUP STUFF'}

soup = BeautifulSoup(url.content, 'html.parser')
contestants = soup.find_all("a", {"class": "category-page__member-link"}, recursive=True)

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

    # {'Name': 'Evie', 'Alliances': ['Yase']}
    return {'Name': contestant_name, 'Alliances': alliance_list}

# contestant_info will be like {"Evie": "Survivor 41", "Yase Alliance",...}
def load_information_to_graph(contestant_info):
    # Check if contestant is already in the graph
    # If contestant not in graph, add to graph
    if contestant_info is not None:
        contestant_name = contestant_info['Name']
        if contestant_name not in contestant_graph:
            # contestant_graph is expecting to be in the format {'Evie': {'Alliances': ['Yase'], 'Seasons': ['Survivor 41'],...}
            contestant_graph[contestant_name] = {'Alliances': contestant_info['Alliances']}

for contestant_html in contestants:
    href = contestant_html['href']
    link = BASE_URL + href
    contestant_or_alliance_soup = get_wiki_page(link)
    graph_entry = scrape_contestant_wiki_page(contestant_or_alliance_soup)
    load_information_to_graph(graph_entry)

# aaron_meredith_info = get_wiki_page('https://survivor.fandom.com/wiki/Aaron_Meredith')
# aaron_meredith_graph_entry = scrape_contestant_wiki_page(aaron_meredith_info)
# load_information_to_graph(aaron_meredith_graph_entry)
print(contestant_graph)