import os
from time import strftime
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, datetime, tzinfo
from pytz import timezone
import logging
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_hash(string1, string2):
    string1 = ''.join(e for e in string1 if e.isalnum())
    string2 = ''.join(e for e in string2 if e.isalnum())
    temp1 = (string1 + string2).lower()
    temp2 = (string2 + string1).lower()
    a = int(''.join(str(ord(c)) for c in temp1))
    b = int(''.join(str(ord(c)) for c in temp2))
    output = str(round((a+b)/2))
    output = output[:8]
    return output

def get_games(panel):
    events = WebDriverWait(panel, timeout=4).until(
        EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='event-list__item']"))
    )
    games = []
    for event in events:
        games.append(event.get_attribute('event-id'))
    return games

def expand_all_panels(driver, actions): 
    try:
        expand_all = WebDriverWait(driver, timeout=4).until(
            EC.element_to_be_clickable(((By.ID, "top-expand-all")))
        )
        actions.move_to_element(expand_all).perform()
        expand_all.click()
        driver.implicitly_wait(1.5)
        expand_all.click()
    except exceptions.TimeoutException:
        logger.error("Error: Timeout while attempting to press panel expand button")
        
        
def find_data(driver, game):
    #get the game winner panel
    try:
        try:
            game_winner_panel = WebDriverWait(driver, timeout=6).until(
                EC.presence_of_element_located(((By.XPATH, "//h3[text() = 'Game Winner']")))
            )
        except:
            logger.error("Error: No game winner panel found for gameID:")
            logger.error(game)
            return {}

        panel_heading = game_winner_panel.find_element_by_xpath('./..')
        if panel_heading.get_attribute('class') == 'panel-heading closed':
            panel_heading.click()
        
        panel = panel_heading.find_element_by_xpath('./..')
        odds_container = panel.find_element_by_xpath(".//div[@class='two-way']")
        odds_conts = odds_container.find_elements_by_xpath(".//odds[@class='odds ng-isolate-scope']")
        team0 = odds_conts[0].find_element_by_xpath(".//span[@class= 'ng-binding ng-scope']").text
        odds0 = int(odds_conts[0].find_element_by_xpath(".//span[@class= 'emphasis ng-binding ng-scope']").text)
        team1 = odds_conts[1].find_element_by_xpath(".//span[@class= 'ng-binding ng-scope']").text
        odds1 = int(odds_conts[1].find_element_by_xpath(".//span[@class= 'emphasis ng-binding ng-scope']").text)
        if odds0 > odds1:
            favorite = (team1, odds1)
            underdog = (team0, odds0)
        else:
            favorite = (team0, odds0)
            underdog = (team1, odds1)
    except Exception as e:
        logger.error("Error: Could not get data for event",game)
        return {}

    eventID = get_hash(team0, team1)

    now = datetime.now(timezone('US/Eastern'))
    output = {
        'Event_ID': eventID, 
        'Contenders': team0 +" : " +team1, 
        'Favorite': favorite, 
        'Underdog': underdog, 
        'Updated': round(now.timestamp()),
        'Updated_Clean': now.strftime('%H:%M:%S'),
        }
    return output

#main
def main(event, context):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
    driver = webdriver.Chrome(chrome_options=chrome_options)
    games = []

    try:
        #connect to DB
        try:
            host = 'odds-db.cwlgxzudqrlz.us-east-2.rds.amazonaws.com'
            user = 'admin'
            password = 'Benbenben108'
            database = 'odds'
        
            conn = pymysql.connect(host=host, user=user, passwd=password, db=database)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(e)

        logger.info("Success: connected to database")
        #SCRAPING LIVE BASKETBALL
        try:
            driver.get('https://plive.ffsvrs.lv/live/?#!/sport/2')
            logger.info("Connected to BetPop Website")
        except:
            logger.error("ERROR: Cant get sportsbook page")
        actions = ActionChains(driver)

        #Expand the panels
        expand_all_panels(driver, actions)

        #Get a list of all the panels (open or closed)
        try:
            panels = WebDriverWait(driver, timeout=4).until(
                EC.presence_of_all_elements_located(((By.XPATH, "//div[@class='panel']")))
            )
        except:
            logger.error("Error: No panels found")

        #Gather game data for each panel
        for panel in panels:
            expand_all_panels(driver, actions)
            #get all games in panel
            games += get_games(panel)
        logger.info("Collected All Games")

        for game in games:
            url = 'https://plive.ffsvrs.lv/live/?#!/event/' + game
            driver.close()
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(url)
            logger.info("Connected to game")
            data = find_data(driver,game)
            if data != {}:
                #check if event id is in event database
                cursor.execute("""SELECT * FROM events WHERE contest_id=%s;""", (int(data.get('Event_ID'))))
                #if event is not in database, insert it
                if cursor.fetchall() == ():
                    cursor.execute("""INSERT INTO events (contest_id, contenders) VALUES (%s,%s);""", (int(data['Event_ID']), data['Contenders']))
                #otherwise add odd to database
                cursor.execute(
                    """INSERT INTO sites 
                        (site_id, site_name, favorite, fav_odds, underdog, under_odds, event_id, updated, updated_clean)
                    VALUES 
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        site_id=VALUES(site_id),
                        site_name=VALUES(site_name), 
                        favorite=VALUES(favorite), 
                        fav_odds=VALUES(fav_odds),
                        underdog=VALUES(underdog),
                        under_odds=VALUES(under_odds),
                        event_id=VALUES(event_id),
                        updated=VALUES(updated),
                        updated_clean=VALUES(updated_clean);""",(
                    1,
                    'BetPop',
                    data.get('Favorite')[0],
                    data['Favorite'][1],
                    data['Underdog'][0],
                    data['Underdog'][1],
                    int(data['Event_ID']),
                    data['Updated'],
                    data['Updated_Clean'],
                ))
                conn.commit()
                logger.info(data)
            else:
                pass 
    finally:
        driver.quit()


