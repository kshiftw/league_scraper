import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re

# https://howpcrules.com/step-by-step-guide-on-scraping-data-from-a-website-and-saving-it-to-a-database/


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

    page_source = driver.page_source
    return page_source

    # for p in all_p:
    #     print(len(p.get_attribute("innerHTML")))


def extract_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    code_soup = soup.find_all('p', attrs={'class': 'p_1_sJ'})

    add_paragraph = ""
    paragraph_list = []
    append = False

    for elem in code_soup:
        # use get_text() to remove <i> tags
        if not append:
            if len(elem.get_text()) < 300:
                add_paragraph += " "
                add_paragraph += elem.get_text()
                append = True
            else:
                paragraph_list.append(elem.get_text())
        else:
            add_paragraph += elem.get_text()
            if len(add_paragraph) > 300:
                append = False
                paragraph_list.append(add_paragraph)
                add_paragraph = ""
    for index, para in enumerate(paragraph_list):
        paragraph_list[index] = para.strip()
        paragraph_list[index] = correct_period(para)
    for para in paragraph_list:
        print(len(para), para)


def correct_period(s):
    # r' + ' searches for multiple spaces to replace with single spaces in s
    # re.sub(r'\.(?! )', '. ', looks for periods without following space character to replace with '. '
    return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', s))


def main():
    driver = browser_driver()
    page_source = access_page(driver)
    extract_data(page_source)


if __name__ == "__main__":
    main()
