import os
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


options = Options()
#options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=os.path.abspath("/Users/benjamingramling/Desktop/Apps/chromedriver"),
options=options)

#SCRAPING LIVE BASKETBALL
driver.get('https://plive.ffsvrs.lv/live/?#!/sport/2')
actions = ActionChains(driver)

def get_games(panel):
    games = WebDriverWait(panel, timeout=4).until(
        EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='event-list__item']"))
    )
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
        

#clik the game winner
def click_game_winner(driver, panel):
    #get name of league
    league = panel.find_element_by_xpath(".//h3[@class='panel-title']").text

    #click on the game winner option in the drop down list of the odds container
    try:
        selector = WebDriverWait(panel, timeout=4).until(
            EC.presence_of_element_located((By.XPATH, ".//div[@class='dropdown market-selector']"))
        )
        try:
            print("Attempting to move to game winnner element for",league)
            actions.move_to_element(selector).perform()
        except:
            print("Failed to move to game winnner element for",league)
        toggler = WebDriverWait(selector, timeout=2).until(
            EC.element_to_be_clickable((By.XPATH, ".//button[@class='market-selector__toggler']"))
        )
        actions.move_to_element(toggler).perform()
        toggler.click()
        try:
            game_winner = WebDriverWait(selector, timeout=2).until(
                EC.element_to_be_clickable((By.XPATH, ".//li[text()='Game Winner']"))
            )
            game_winner.click()
        except exceptions.TimeoutException:
            print("Error on panel ",league,": Timeout while trying to click GameWinner. Reclicking toggler.")
            toggler.click()
    except exceptions.TimeoutException:
        print("Error on panel ",league,": Timeout while trying to click toggler/selector.")
        pass
    except exceptions.WebDriverException:
        print("Error on panel ",league,": WebdriverException")
        pass
        
def find_data(game):
    #find teams
    team1 = game.find_element_by_xpath(".//p[@data-testid='top-team-details']").get_attribute('title')
    team2 = game.find_element_by_xpath(".//p[@data-testid='bottom-team-details']").get_attribute('title')
    contest = [team1, team2]

    #find odds
    try:
        odds_container = WebDriverWait(game, timeout=4).until(
            EC.presence_of_element_located(((By.XPATH, ".//div[@class='offerings market--two-row market-3']")))
        )
        odds_conts = odds_container.find_elements_by_xpath(".//span[@class='emphasis']")
        odds = [int(odds_conts[0].text), int(odds_conts[1].text)]
        if odds[0] > odds[1]:
            favorite = {team2: odds[1]}
            underdog = {team1: odds[0]}
        else:
            favorite = {team1: odds[0]}
            underdog = {team2: odds[1]}
    except:
        print("Error: Could not get odds for",team1, "vs", team2)
        favorite = {}
        underdog = {}
        pass

    output = pd.Series({'Sport': 'Basketball', 'Contenders': contest, 'Favorite': favorite, 'Underdog': underdog})
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
        #click game winner
        click_game_winner(driver, panel)

        #get all games in panel
        try:
            games = get_games(panel)
        except:
            expand_all_panels(driver)
            try:
                get_games(panel)
            except:
                print("Error: could not get games for this panel")

        #add games to list
        for game in games:
            db = db.append(find_data(game), ignore_index = True)

finally:
    driver.quit()
    db.to_csv('~/Desktop/output.csv', index = False, header=True)