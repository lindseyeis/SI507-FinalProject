from flask import Flask, render_template

import FinalProject
import scraper

app = Flask(__name__)
app.debug = True

@app.route('/')
def dropdown():
    print("starting to generate dropdown")
    # scraper.scrape_all_contestant_and_alliance_pages()
    FinalProject.get_all_contestants_and_alliances_mongo()
    print("done scraping")
    contestants_and_alliances = FinalProject.contestant_and_alliance_graph
    contestants = FinalProject.contestants_list
    alliances = FinalProject.alliances_list
    FinalProject.mongo_entries()
    FinalProject.get_path_to_victory("Aaron Meredith")
    return render_template('website.html', contestantsAndAlliances=contestants_and_alliances.keys(), contestants_page=contestants, alliances_page=alliances)

@app.route('/onContestantChanged')
def onContestantChanged():
    print("ON CONTESTANT CHANGED")
# Use 'FLASK_APP=website.py FLASK_ENV=development flask run' to run it