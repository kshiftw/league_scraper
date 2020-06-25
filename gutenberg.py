from pymongo import MongoClient
import os


def access_book():
    rootdir = 'D:/Gutenberg SF'
    count = 0

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            if count == 1:
                return

            if filepath.endswith(".txt"):
                count += 1
                print(filepath)
                get_text(filepath)


def get_text(filepath):
    title = ''
    author = ''

    with open(filepath, 'r') as document:
        for line in document:
            print(line)


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
    access_book()


if __name__ == "__main__":
    main()