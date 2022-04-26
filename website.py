from flask import Flask, render_template, request, jsonify
import FinalProject
import scraper



app = Flask(__name__)
app.debug = True

@app.route('/')
def dropdown():
    # scraper.scrape_all_contestant_and_alliance_pages()
    FinalProject.get_all_contestants_and_alliances_mongo()
    contestants_and_alliances = FinalProject.contestant_and_alliance_graph
    contestants = FinalProject.contestants_list
    alliances = FinalProject.alliances_list
    FinalProject.mongo_entries()
    return render_template('website.html', contestantsAndAlliances=contestants_and_alliances.keys(), contestants_page=contestants, alliances_page=alliances)

@app.route('/onContestantChanged')
def onContestantChanged():
    print("ON CONTESTANT CHANGED")
# Use 'FLASK_APP=website.py FLASK_ENV=development flask run' to run it

@app.route('/handleContestantChange', methods = ['POST'])
def handleContestantChange():
    contestant_or_alliance = request.form['contestant']
    print(contestant_or_alliance)
    if contestant_or_alliance in FinalProject.contestants_list:
        contestant_info = FinalProject.contestant_and_alliance_graph[contestant_or_alliance]
        contestant_alliances = ', '.join(contestant_info["Alliances"])
        contestant_seasons = ''
        seasons = contestant_info['Seasons']
        for season in seasons:
            contestant_seasons += season + ', Ranked ' + seasons[season] + "</br>"
        contestant_path_to_victory = ' -> '.join(FinalProject.get_path_to_victory(contestant_or_alliance))
        return f"<h1>Contestant Name: {contestant_or_alliance}</h1></br><h1>Contestant Alliances: {contestant_alliances}</h1></br><h1>Contestant Seasons: {contestant_seasons}</h1></br><h1>Contestant Path to Victory: {contestant_path_to_victory}</h1>"
    elif contestant_or_alliance in FinalProject.alliances_list:
        alliance_info = FinalProject.contestant_and_alliance_graph[contestant_or_alliance]
        alliance_members = ', '.join(alliance_info)
        print(alliance_members)
        return f"<h1>Alliance Name: {contestant_or_alliance}</h1></br><h1>Alliance Members: {alliance_members}</h1>"
    else:
        return f"<h1></h1>"