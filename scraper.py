import FinalProject
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://survivor.fandom.com'
CONTESTANT_URL = '/wiki/Category:Survivor_(U.S.)_Contestants'
ALLIANCE_URL = '/wiki/Category:Alliances'

# This function returns the beautiful soup for a contestant or alliance
def get_wiki_page(contestant_or_alliance_url):
    # {'Evie': 'beautiful soup info here'}
    # {'Yase Alliance': 'beautiful soup here'}
    if contestant_or_alliance_url not in FinalProject.wiki_html_cache:
        contestant_link = requests.get(contestant_or_alliance_url)
        contestant_soup = BeautifulSoup(contestant_link.content, 'html.parser')
        FinalProject.wiki_html_cache[contestant_or_alliance_url] = contestant_soup
    return FinalProject.wiki_html_cache[contestant_or_alliance_url]


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

def load_contestant_information_to_graph(contestant_info):
    if contestant_info is not None:
        contestant_name = contestant_info['Name']
        if contestant_name not in FinalProject.contestant_and_alliance_graph:
            FinalProject.contestant_and_alliance_graph[contestant_name] = {'Alliances': contestant_info['Alliances'], 'Seasons': contestant_info['Seasons']}

def load_alliance_information_to_graph(alliance_info):
    if alliance_info is not None:
        alliance_name = alliance_info['Alliance Name']
        if alliance_name not in FinalProject.contestant_and_alliance_graph:
            FinalProject.contestant_and_alliance_graph[alliance_name] = alliance_info['Members']

def scrape_all_contestant_and_alliance_pages():
    contestant_url = requests.get(BASE_URL + CONTESTANT_URL)
    alliance_url = requests.get(BASE_URL + ALLIANCE_URL)

    all_contestants_soup = BeautifulSoup(contestant_url.content, 'html.parser')
    alliance_soup = BeautifulSoup(alliance_url.content, 'html.parser')

    contestants = []
    contestants.extend(all_contestants_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True))

    pagination_buttons = all_contestants_soup.find("div", {"class": "category-page__pagination"})
    next_button = pagination_buttons.find("a", {"class": "category-page__pagination-next wds-button wds-is-secondary"})

    while next_button is not None:
        next_button_link = next_button['href']
        contestant_page_url = requests.get(next_button_link)
        all_contestants_soup = BeautifulSoup(contestant_page_url.content, 'html.parser')
        contestants.extend(all_contestants_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True))
        pagination_buttons = all_contestants_soup.find("div", {"class": "category-page__pagination"})
        next_button = pagination_buttons.find("a", {"class": "category-page__pagination-next wds-button wds-is-secondary"})

    alliances = alliance_soup.find_all("a", {"class": "category-page__member-link"}, recursive=True)
    for contestant_html in contestants:
        href = contestant_html['href']
        link = BASE_URL + href
        contestant_or_alliance_soup = get_wiki_page(link)
        graph_entry = scrape_contestant_wiki_page(contestant_or_alliance_soup)
        load_contestant_information_to_graph(graph_entry)
        print(graph_entry)
        if graph_entry is not None and graph_entry['Name'] is not None:
            FinalProject.contestants_list.append(graph_entry['Name'])

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
            FinalProject.alliances_list.append(graph_entry['Alliance Name'])