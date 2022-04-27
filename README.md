# SI507-FinalProject
Survivor Alliance Browser for UMSI SI507

The program runs off of FinalProject.py, scraper.py, website.py, website.html and website.css. (website.html is located in the templates folder and website.css is located in the static/styles folder)

Make sure you are on a version of Python3 and do a pip3 install of the following: BeautifulSoup4, requests, pymongo, certifi, flask, dnspython

IN ORDER TO CONNECT TO MONGODB AND MAKE THE CODE WORK, go to FinalProject.py and insert the connection string, that I provided in the PDF submitted on Canvas, on line 10.

Open website.py and use the following command to begin running flask: FLASK_APP=website.py FLASK_ENV=development flask run

You may need to add Flask to your PATH variable for this command to run. You should be prompted in the VSCode terminal if this is the case. The command to add Flask to your PATH is: PATH=$PATH:(directory name here). For example, mine was PATH=$PATH:/Users/lindseyeisenshtadt/Library/Python/3.10/bin

You can switch between getting data from the web crawler/scraper and getting data from the MongoDB database. 
To use scraping, in website.py, uncomment line 14 and comment line 15, or vice versa to use the MongoDB data. 
By default, MongoDB is used, so it will take about 30 seconds to load the website. 
Using web scraping will make it take around 3 minutes to load. 
The graph, shown at the bottom of the site, will display the connection between the contestant that has been entered and the winner.

When the user opens the website, they will see a four ways to interact with the site and select/display the data:
  1. The user can select an alliance that will display the alliance name and alliance members.
  2. The user can select a contestant that will display the contestant name, the alliance(s) they were in, their season and ranking, and the path to            victory.
  3. The user can press the ‘Random Contestant’ button which will randomly select a contestant and display the same information as listed above.
  4. The user can press the ‘Random Alliance' button which will randomly select an alliance and display the same information as listed above.
If a user selects a contestant then at the bottom of the page, the graph information will be displayed so users can see the connection between the selected player and the winner. This will be displayed at ‘Path to Victory”

In the command line in VSCode, after opening website.py, the user will run the command ‘FLASK_APP=website.py FLASK_ENV=development flask run’ to prompt flask to open the website and click on the host server link to open it. The host server should be something like: http://127.0.0.1:5000
