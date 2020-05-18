from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
import time
import csv


def browser_driver():
    """ Configure the browser driver that will access the urls.

    :precondition: Chrome Driver must be installed and the path is on hand https://sites.google.com/a/chromium.org/chromedriver/downloads
    :return: the driver to be used
    """
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    # set to headless so that chrome won't display the browser
    chrome_options.add_argument('--headless')
    driver = Chrome("C:/Users/Kirk/PycharmProjects/league_scraper/chromedriver_win32/chromedriver.exe", options=chrome_options)
    return driver


def get_urls(driver):
    """ Navigates the dynamic page and collects the list of urls to short stories.

    :param driver: the chrome driver
    :return: url_set is a set of href taken from each <a> tag
    """
    main_page = "https://universe.leagueoflegends.com/en_US/explore/short-stories/newest/"
    url_set = set()
    driver.get(main_page)

    # https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    SCROLL_PAUSE_TIME = 1.0

    # Get the end of page height by first scrolling all the way to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0

    # Scroll back to the top of the page
    driver.execute_script("window.scrollTo(0, 0);")

    # Because the cards are dynamically loaded when scrolling down the webpage, we navigate the page by scrolling down
    # 1000px and reading the a tag's href attributes until we reach the bottom of the page
    while True:
        # Scroll down by 1000px every loop
        driver.execute_script("window.scrollTo(0, window.scrollY + 1000)")
        current_height += 1000

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # every short story card has the same class name, so that's what we search for
        code_soup = soup.find_all('li', attrs={'class': 'Card_CCcI Result_2bn_'})
        # each <li> element has an <a> tag that redirects to the short story's page
        for li in code_soup:
            a_tag = li.find("a", recursive=False, href=True)
            url_set.add(a_tag['href'])
        # once we have scrolled to the bottom of the page, exit the loop
        if current_height >= last_height:
            break
    return url_set


def access_page(driver, url_set):
    """ Access the main page where we will gather a list of all short story urls.

    :param driver: the chrome driver
    :param url_set: a set of the hrefs to all short stories
    """
    base_url = "https://universe.leagueoflegends.com"
    for page in url_set:
        # append the href path to the base url
        url = base_url + page
        driver.get(url)
        page_source = driver.page_source

        # for each short story, extract the excerpts
        extract_data(page_source, url)


def extract_data(page_source, url):
    """ Extract the excerpts from the short story.

    :param page_source: page source of the short story page
    :param url: the url of the page
    """
    soup = BeautifulSoup(page_source, 'html.parser')

    # get the title of the short story
    if soup.find('h1', attrs={'class': 'title_121J'}):
        title = soup.find('h1', attrs={'class': 'title_121J'}).get_text()
    else:
        # if it doesn't exist (a couple pages did not follow the same format)
        title = ""

    # get all paragraphs in the short story
    if soup.find_all('p', attrs={'class': 'p_1_sJ'}):
        p_soup = soup.find_all('p', attrs={'class': 'p_1_sJ'})
    else:
        # if no <p> with the class are found (a couple pages did not follow the same format), then don't bother
        # extracting the page
        return

    add_paragraph = ""
    paragraph_list = []
    append = False

    # for each paragraph, check that it isn't too short (if < 300 characters)
    # if it is too short, save it so that it can be appended to the next paragraph in the list
    # use append variable to keep track of if there is a paragraph from the previous loop to append
    for elem in p_soup:
        # use elem.get_text() to remove all html tags (ie. <i>)
        if not append:
            if len(elem.get_text()) < 300:
                add_paragraph += " "
                add_paragraph += elem.get_text()
                append = True
            else:
                # if it is long enough, append it to the paragraph_list
                paragraph_list.append(elem.get_text())
        else:
            # if there is already something in add_paragraph, append the current paragraph to it
            add_paragraph += elem.get_text()
            if len(add_paragraph) > 300:
                append = False
                paragraph_list.append(add_paragraph)
                add_paragraph = ""
    # cleaning up the formatting
    for index, para in enumerate(paragraph_list):
        paragraph_list[index] = para.strip()
        paragraph_list[index] = correct_period(para)

    row_list = []
    # create a list of rows that will be inserted into the csv file
    for para in paragraph_list:
        row_list.append([url, title, para])
    write_csv(row_list)


def write_csv(row_list):
    """ Writes all data in row_list into a csv file

    :param row_list: list containing rows to be inserted into the csv file
    """
    # use 'a' for append, set newline so that it doesn't have an extra line, set encoding to include unicode characters
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


if __name__ == "__main__":
    main()
