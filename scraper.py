import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def browser_driver():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless')
    driver = Chrome("C:/Users/Kirk/PycharmProjects/league_scraper/chromedriver_win32/chromedriver.exe", options=chrome_options)
    return driver


def access_page(driver):
    url = "https://universe.leagueoflegends.com/en_US/story/perennial/"
    driver.get(url)
    all_p = driver.find_elements_by_xpath("//p[@class='p_1_sJ']")
    print("length", len(all_p))
    for p in all_p:
        print(p.get_attribute("innerHTML"))
    page_source = driver.page_source
    return page_source


def extract_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    

def main():
    driver = browser_driver()
    page_source = access_page(driver)
    extract_data(page_source)


if __name__ == "__main__":
    main()
