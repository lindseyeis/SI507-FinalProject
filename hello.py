from flask import Flask, render_template

import FinalProject
app = Flask(__name__)
app.debug = True

@app.route('/')
def dropdown():
    print("starting to generate dropdown")
    FinalProject.scrape_all_contestant_and_alliance_pages()
    print("done scraping")
    contestants_and_alliances = FinalProject.contestant_and_alliance_graph
    contestants = FinalProject.contestants_list
    alliances = FinalProject.alliances_list
    FinalProject.mongo_entries()
    FinalProject.get_path_to_victory("Aaron Meredith")
    return render_template('hello.html', contestantsAndAlliances=contestants_and_alliances.keys(), contestants_page=contestants, alliances_page=alliances)
    # return render_template('hello.html', contestants_page=contestants)
    # return render_template('hello.html', alliances_page=alliances)

@app.route('/onContestantChanged')
def onContestantChanged():
    print("ON CONTESTANT CHANGED")
# Use 'FLASK_APP=hello.py FLASK_ENV=development flask run' to run it