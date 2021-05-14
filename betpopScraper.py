import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=os.path.abspath("/Users/benjamingramling/Desktop/Apps/chromedriver"),
options=options)
games = []

#SCRAPING LIVE BASKETBALL
driver.get('https://plive.ffsvrs.lv/live/?#!/sport/2')
actions = ActionChains(driver)

def get_games(panel):
    events = WebDriverWait(panel, timeout=4).until(
        EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='event-list__item']"))
    )
    games = []
    for event in events:
        games.append(event.get_attribute('event-id'))
    return games

def expand_all_panels(driver): 
    try:
        expand_all = WebDriverWait(driver, timeout=4).until(
            EC.element_to_be_clickable(((By.ID, "top-expand-all")))
        )
        actions.move_to_element(expand_all).perform()
        expand_all.click()
        driver.implicitly_wait(1.5)
        expand_all.click()
    except exceptions.TimeoutException:
        print("Error: Timeout while attempting to press panel expand button")
        
        
def find_data(driver, game):
    #get the game winner panel
    try:
        try:
            game_winner_panel = WebDriverWait(driver, timeout=6).until(
                EC.presence_of_element_located(((By.XPATH, "//h3[text() = 'Game Winner']")))
            )
        except:
            print("Error: No game winner panel found for gameID:",game)
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
            favorite = {team1: odds1}
            underdog = {team0: odds0}
        else:
            favorite = {team0: odds0}
            underdog = {team1: odds1}
    except Exception as e:
        print("Error: Could not get data for event",game)
        print(e)
        return {}

    output = pd.Series({'Sport': 'Basketball', 'Contenders': [team0, team1], 'Favorite': favorite, 'Underdog': underdog})
    return output

#create dataframe
db = pd.DataFrame(columns=['Sport','Contenders', 'Favorite','Underdog'])

#main
try:
    #Expand the panels
    expand_all_panels(driver)

    #Get a list of all the panels (open or closed)
    try:
        panels = WebDriverWait(driver, timeout=4).until(
            EC.presence_of_all_elements_located(((By.XPATH, "//div[@class='panel']")))
        )
    except:
        print("Error: No panels found")

    #Gather game data for each panel
    for panel in panels:
        #get all games in panel
        games += get_games(panel)

    for game in games:
        url = 'https://plive.ffsvrs.lv/live/?#!/event/' + game
        driver.get(url)
        data = find_data(driver,game)
        if isinstance(data, pd.Series):
            db = db.append(data, ignore_index = True)
            db.to_csv('~/Desktop/output.csv', index = False, header=True)
        else:
            pass
        
finally:
    driver.quit()