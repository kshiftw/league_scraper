"""
https://www.gutenberg.org/wiki/Gutenberg:The_CD_and_DVD_Project#Downloading_Via_FTP
https://www.gutenberg.org/browse/scores/top#books-last1
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

    # find ol element
    # get all li elements under ol element
    # get href from a tag
    # book_number =  number after second / in href
    # https://www.gutenberg.org/files/1342/1342-h/1342-h.htm
    # url = "https://www.gutenberg.org/files/" + book_number + "/" + book_number + "-h/" + book_number + "-h.htm"
    # url_set.add(url)

    for _ in range(100):


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

    # get the title of the short story

    # get first <pre> element
    # find "Title: " and "Author: "
    # or
    # find first <h1> and first <h2>

    # find all <p>
    # if 300 < length < 500, add to database

    # remove underscore



    if soup.find('h1', attrs={'class': 'title_121J'}):
        title = soup.find('h1', attrs={'class': 'title_121J'}).get_text()
    else:
        # if it doesn't exist (a couple pages did not follow the same format)
        title = ""

    # get the author of the short story
    if soup.find('h2', attrs={'class': 'subtitle_XESa'}):
        author = soup.find('h2', attrs={'class': 'subtitle_XESa'}).get_text()
        author = remove_by(author)
    else:
        # if it doesn't exist (a couple pages did not follow the same format)
        author = ""

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
                add_paragraph += elem.get_text()
                append = True
            else:
                # if it is long enough, append it to the paragraph_list
                paragraph_list.append(elem.get_text())
        else:
            # if there is already something in add_paragraph, append the current paragraph to it
            add_paragraph += " "
            add_paragraph += elem.get_text()
            if len(add_paragraph) > 300:
                append = False
                paragraph_list.append(add_paragraph)
                add_paragraph = ""
    # cleaning up the formatting
    for index, para in enumerate(paragraph_list):
        paragraph_list[index] = para.strip()

    row_list = []
    # create a list of rows that will be inserted into the csv file
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


if __name__ == "__main__":
    main()
