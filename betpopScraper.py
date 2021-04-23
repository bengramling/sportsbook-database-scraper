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


options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=os.path.abspath("/Users/benjamingramling/Desktop/Apps/chromedriver"),
options=options)

#SCRAPING LIVE BASKETBALL
driver.get('https://plive.ffsvrs.lv/live/?#!/sport/2')
try:
    try:
        panels = WebDriverWait(driver, timeout=4).until(
            EC.presence_of_all_elements_located(((By.XPATH, "//div[@class='panel']")))
        )
        #print(panels)
    except:
        print("no panels found")

    for panel in panels:
        try:
            #print(panel.text)
            closed_heading = WebDriverWait(panel, timeout=4).until(
                EC.visibility_of_element_located((By.XPATH, ".//div[@class='panel-heading closed']"))
            )
            print(panel.text, "Panel Closed. Opening Panel")
            button = closed_heading.find_element_by_xpath('*')
            button.click() 
            #print("opened panel")
        except:
            print("could not open panel / panel already open")
            pass

        #get list of games
        games = WebDriverWait(panel, timeout=5).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='event-list__item']"))
            )
        for game in games:
            top_team = game.find_element_by_xpath(".//p[@data-testid='top-team-details']")
            print("Team 1: ", top_team.get_attribute('title'))
            bottom_team = game.find_element_by_xpath(".//p[@data-testid='bottom-team-details']")
            print("Team 2: ", bottom_team.get_attribute('title'))

        try:
            selector = WebDriverWait(panel, timeout=4).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='dropdown market-selector']"))
            )
            toggler = WebDriverWait(selector, timeout=2).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[@class='market-selector__toggler']"))
            )
            toggler.click()
            print("clicked on toggler")
            game_winner = WebDriverWait(selector, timeout=4).until(
                EC.element_to_be_clickable((By.XPATH, ".//li[text()='Game Winner']"))
            )
            game_winner.click()
            print("clicked on game winner")
        except exceptions.TimeoutException:
            print("the request timed out")

        finally:
            print("done")

finally:
    driver.quit()