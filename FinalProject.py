import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://survivor.fandom.com'

url = requests.get(BASE_URL + '/wiki/Category:Survivor_(U.S.)_Contestants')

soup = BeautifulSoup(url.content, 'html.parser')
contestants = soup.find_all("a", {"class": "category-page__member-link"}, recursive=True)

for contestant_html in contestants:
    href = contestant_html['href']
    link = BASE_URL + href
    contestant_url = requests.get(link)
    contestant_soup = BeautifulSoup(contestant_url.content, 'html.parser')
    print(contestant_soup.prettify())
