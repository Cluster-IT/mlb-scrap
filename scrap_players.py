import re
import requests
import logging
from bs4 import BeautifulSoup, NavigableString
from datetime import date

file_name = "scrap_%s.log" % (date.today().strftime("%d_%m_%Y"))
logging.basicConfig(
    filename=file_name, 
    filemode='w', 
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%d-%b-%y %H:%M:%S'
)


URL = "https://www.mlb.com"

# Logic to fetch data from the URL
res = requests.get(URL+'/players')
soup = BeautifulSoup(res.text)
anchors = soup.findAll("a", {"class" : "p-related-links__link"})
teamdata = {}

# Picking all the anchors having the players information along with name and URL
logging.info("Process of Fetching data started")
for i, row in enumerate(anchors):
    teamdata[i] = {"url" : row.get("href"),  "name" : row.contents[0]}

logging.info("Retrieved players information")
#Fetching the information of Individual players
for row, data in teamdata.items():
    logging.info("Fetching player information:: %s" % (data['name']))
    player_url = URL+data.get("url").strip()
    try:
        resp = requests.get(player_url)
    except Exception as e:
        logging.error("Error while Fetching player information :: %s" % (data['name']))

    # Storing the data in temporary file as the player information was not loading while rendering.
    fp = open("/tmp/mlbdata.html", "w")
    fp.write(resp.text)
    fp.close()

    try:
        soup = BeautifulSoup(open("/tmp/mlbdata.html"), "html.parser")
    except Exception as e:
        logging.error("Error while parsing player information :: %s" % (data['name']))

    # Collected the Header information include the below
    # Photo, Name, T-Shirt No., Height, Weight, Age, BT.

    try:
        header = soup.find("main").find("section").find("header").find("div")
    except Exception as e:
        print("Error while Retriving data for the Player::", data['name'])
        pass
    try:
        img_url = header.find("img").get('src')
        teamdata[row]['image'] = img_url
    except Exception as e:
        logging.error("Error while Retriving player information :: %s" % (data['name']))

    try:
        shirt_no = header.find("div").find("span", "player-header--vitals-number").text
        teamdata[row]['t-shirt-no'] = shirt_no
    except Exception as e:
        logging.error("Error while Retriving player T-Shirt No :: %s" % (data['name']))
    
    
    field_data = header.find("div").find("ul")

    if field_data:
        try:
            age = field_data.find("li", "player-header--vitals-age").text
        except Exception as e:
            logging.error("Error while Retriving player Age :: %s" % (data['name']))
        teamdata[row]['age'] = age.split('Age:')[-1].strip()
    else:
        logging.error("Error while Retriving player Age :: %s" % (data['name']))
    
    if field_data:
        try:
            height_weight = field_data.find("li", "player-header--vitals-height").text
        except Exception as e:
            logging.error("Error while Retriving player Height & Weight :: %s" % (data['name']))
        height_weight = height_weight.split("/")

        teamdata[row]['height'] = height_weight[0]
        teamdata[row]['weight'] = height_weight[1]
    else:
        logging.error("Error while Retriving player Height & Weight :: %s" % (data['name']))

    try:
        bt_data = field_data.find_all(text=re.compile('B/T'))
        teamdata[row]['bt'] = bt_data[0].split(':')[-1].strip()
    except Exception as e:
        logging.error("Error while Retriving player B/T info :: %s" % (data['name']))

    # Fetching Body container for FullName and Borndate.

    try:
        body = soup.find("main").find("section", {"class": "section-container"})
        dob_body = body.find("div", {"class": "player-bio"})
    except Exception as e:
        logging.error("Error while Retriving player DOB info :: %s" % (data['name']))

    if dob_body:
        name_details = dob_body.findAll("li")
        for rec in name_details:
            if 'fullname' in rec.text.lower():
                teamdata[row]['full_name'] = rec.text.split(':')[-1].strip()
            if 'born' in rec.text.lower():
                teamdata[row]['born_date'] = rec.text.split("\n")[0].split(":")[-1].strip()
    else:
        logging.error("Error retriving DOB of player :: %s" % (data['name']))
    logging.info("Fetched player information :: %s" % (data['name']))
    logging.info("--------------------------------------------------")

# Process to store the data in database