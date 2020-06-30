"""
Kirk Wong

This module uses Selenium and BeautifulSoup to retrieve the top 100 Ebooks from Project Gutenberg
https://www.gutenberg.org/browse/scores/top and extract excerpts from the ebooks. After the data is extracted and
cleaned up, it is written into as documents in MongoDB.
"""
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


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
    main_page = "https://www.gutenberg.org/browse/scores/top"
    url_set = set()
    driver.get(main_page)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the first ol element, which is the "Top 100 EBooks yesterday" category
    if soup.find('ol'):
        ol_soup = soup.find('ol')

        # Gets all 100 elements
        li_soup = ol_soup.findChildren('li', recursive=False)

        # For each li element, get the book number and generate the direct link to the book
        for li in li_soup:
            a_tag = li.find("a", recursive=False, href=True)
            href = a_tag['href']
            book_number = href.split('/')[-1]
            url = "https://www.gutenberg.org/files/" + book_number + "/" + book_number + "-h/" + book_number + "-h.htm"
            url_set.add(url)
    return url_set


def access_page(driver, url_set):
    """ Access the main page where we will gather a list of all short story urls.

    :param driver: the chrome driver
    :param url_set: a set of the hrefs to all short stories
    """
    for url in url_set:
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

    # Get the title
    if soup.find('h1'):
        title = soup.find('h1').get_text().strip()
    else:
        # if it doesn't exist
        title = ""

    # Get the author
    if soup.find('h2'):
        author = soup.find('h2').get_text().strip()
        author = remove_by(author)
    else:
        # if it doesn't exist
        author = ""

    # Get all paragraphs
    if soup.find_all('p'):
        p_soup = soup.find_all('p')
    else:
        # if no <p> with the class are found, then don't bother extracting the page
        return

    paragraph_list = []

    for elem in p_soup:
        # use elem.get_text() to remove all html tags (ie. <i>)
        # Only get paragraphs within a certain length range
        if 300 < len(elem.get_text()) < 500:
            paragraph_list.append(elem.get_text().replace('\n', ' ').replace('       ', ' '))
    # cleaning up the formatting
    for index, para in enumerate(paragraph_list):
        paragraph_list[index] = para.strip()

    row_list = []
    # create a list of rows that will be inserted into the database
    for para in paragraph_list:
        row = {
            'url': url,
            'title': title,
            'author': author,
            'excerpt': para,
            'category': "gutenberg",
            'leaderboard': [],
            }
        row_list.append(row)
    insert_db(row_list)


def remove_by(s):
    if s[0:2].lower() == "by":
        return s[3:]
    else:
        return s


def insert_db(row_list):
    """ Inserts rows as documents into MongoDB.

    :param row_list: a list of documents to be inserted
    """
    client = MongoClient(port=27017)
    # Database name is "type-"
    db = client['type-']
    for row in row_list:
        # Database Collection name is "gutenberg_excerpts"
        db.gutenberg_excerpts.insert_one(row)


def main():
    driver = browser_driver()
    url_set = get_urls(driver)
    access_page(driver, url_set)

    # test access to single page
    # access_page(driver, {'https://www.gutenberg.org/files/972/972-h/972-h.htm'})


if __name__ == "__main__":
    main()
