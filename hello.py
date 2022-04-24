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
    return render_template('hello.html', contestantsAndAlliances=contestants_and_alliances.keys())

# Use 'FLASK_APP=hello.py FLASK_ENV=development flask run' to run it