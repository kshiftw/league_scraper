import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
import time
import csv

# https://howpcrules.com/step-by-step-guide-on-scraping-data-from-a-website-and-saving-it-to-a-database/


def browser_driver():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    # chrome_options.add_argument('--headless')
    driver = Chrome("C:/Users/Kirk/PycharmProjects/league_scraper/chromedriver_win32/chromedriver.exe", options=chrome_options)
    return driver


def get_urls(driver):
    main_page = "https://universe.leagueoflegends.com/en_US/explore/short-stories/newest/"

    url_set = set()

    driver.get(main_page)

    # https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    SCROLL_PAUSE_TIME = 1.0

    # Get scroll height
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    driver.execute_script("window.scrollTo(0, 0);")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, window.scrollY + 1000)")
        current_height += 1000

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        code_soup = soup.find_all('li', attrs={'class': 'Card_CCcI Result_2bn_'})
        for div in code_soup:
            a_tag = div.find("a", recursive=False, href=True)
            url_set.add(a_tag['href'])
        if current_height >= last_height:
            break
    return url_set


def access_page(driver, url_set):
    base_url = "https://universe.leagueoflegends.com"
    for page in url_set:
        url = base_url + page
        driver.get(url)
        page_source = driver.page_source
        extract_data(page_source, url)

    # driver.get("https://universe.leagueoflegends.com/en_US/story/star-guardian-starfall/")
    # page_source = driver.page_source
    # extract_data(page_source, 'url')


def extract_data(page_source, url):
    soup = BeautifulSoup(page_source, 'html.parser')
    if soup.find('h1', attrs={'class': 'title_121J'}):
        title = soup.find('h1', attrs={'class': 'title_121J'}).get_text()
    else:
        title = ""
    if soup.find_all('p', attrs={'class': 'p_1_sJ'}):
        p_soup = soup.find_all('p', attrs={'class': 'p_1_sJ'})
    else:
        return

    add_paragraph = ""
    paragraph_list = []
    append = False
    for elem in p_soup:
        # use elem.get_text() to remove all html tags (ie. <i>)
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

    row_list = []
    for para in paragraph_list:
        row_list.append([url, title, para])
    write_csv(row_list)


def write_csv(row_list):
    with open('excerpts.csv', 'a', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)


def correct_period(s):
    # https://stackoverflow.com/questions/29506718/having-trouble-adding-a-space-after-a-period-in-a-python-string/29507362
    # r' + ' searches for multiple spaces to replace with single spaces in s
    # re.sub(r'\.(?! )', '. ', looks for periods without following space character to replace with '. '
    return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', s))


def main():
    driver = browser_driver()
    url_set = get_urls(driver)
    access_page(driver, url_set)

    # driver = browser_driver()
    # access_page(driver, {"test"})


if __name__ == "__main__":
    main()
