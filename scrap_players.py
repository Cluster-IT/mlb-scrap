import requests
from bs4 import BeautifulSoup, NavigableString

URL = "https://www.mlb.com"

# Logic to fetch data from the URL
res = requests.get(URL+'/players')
soup = BeautifulSoup(res.text)
anchors = soup.findAll("a", {"class":"p-related-links__link"})
teamdata = {}

# Picking all the anchors having the players information along with name and URL

for i, row in enumerate(anchors):
    teamdata[i] = {"url": row.get("href"),  "name": row.contents[0]}


#Fetching the information of Individual players
for row, data in teamdata.items():
    player_url = URL+data.get("url").strip()
    try:
        resp = requests.get(player_url)
    except Exception as e:
        print("Error fetching data for the Player:::", data['name'])
    
    # Storing the data in temporary file as the player information was not loading while rendering.
    fp = open("/tmp/mlbdata.html", "w")
    fp.write(resp.text)
    fp.close()

    try:
        soup = BeautifulSoup(open("/tmp/mlbdata.html"), "html.parser")
    except Exception as e:
        print("Error fetching data:::", e)

    # Collected the Header information include the below
    # Photo, Name, T-Shirt No., Height, Weight, Age, BT.

    try:
        header = soup.find("main").find("section").find("header").find("div")
    except Exception as e:
        print("Error while Retriving data for the Player::", data['name'])
        pass
    try:
        img_url = header.find("img").get('src')
    except Exception as e:
        print("Error while Retriving data for the Player::", data['name'])

    teamdata[row]['t-shirt-no'] = header.find("div").find("span", "player-header--vitals-number").text
    teamdata[row]['image'] = img_url
    field_data = header.find("div").find("ul")
    
    for field in field_data:
        if not isinstance(field, NavigableString):
            if 'age' in field.text.lower():
                teamdata[row]['age'] = field.text

            if 'B/T' in field.text:
                teamdata[row]['bt'] = field.text

            if 'P' not in field.text and 'B/T' not in field.text and 'Age' not in field.text:
                height_weight = field.text.split('/')
                teamdata[row]['height'] = height_weight[0]
                teamdata[row]['weight'] = height_weight[1]

    # Fetching Body container for FullName and Borndate.

    body = soup.find("main").find("section", {"class":"section-container"})
    dob_body = body.find("div", {"class":"player-bio"})

    name_details = dob_body.findAll("li")
    for rec in name_details:
        if 'fullname' in rec.text.lower():
            teamdata[row]['full_name'] = rec.text.split(':')[-1].strip()
        if 'born' in rec.text.lower():
            teamdata[row]['born_date'] = rec.text.split("\n")[0].split(":")[-1].strip()


#Process to store the data in database.
