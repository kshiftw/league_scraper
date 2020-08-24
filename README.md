# Description
Python scripts used to extract excerpts that were used for Typedash: https://github.com/kshiftw/type-. Both scripts utilize similar technologies and concepts but are different in the specifics of how they scrape the website. 

#### League of Legends Short Stories - scraper.py 
This script uses Selenium and BeautifulSoup to navigate the League of Legends universe page https://universe.leagueoflegends.com/en_US/explore/short-stories/newest/ and extracts excerpts from all short stories. After the data is extracted and cleaned up, it is written into as documents in MongoDB.

#### Project Gutenberg - gutenberg.py
This script uses Selenium and BeautifulSoup to retrieve the top 100 Ebooks from Project Gutenberg https://www.gutenberg.org/browse/scores/top and extract excerpts from the ebooks. After the data is extracted and cleaned up, it is written into as documents in MongoDB.
