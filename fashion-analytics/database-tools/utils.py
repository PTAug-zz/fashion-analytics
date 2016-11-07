from bs4 import BeautifulSoup

def write_in_file(name_of_file: str, content):
    """
    Writes the content in a file of name name_of_file.
    """
    print("Creation of file " + name_of_file)
    file = open(name_of_file, "w")
    print("Writing...")
    file.write(content)
    file.close()
    print("Saving in file successful!")


def get_soup_from_file(filename: str):
    """
    Returns the BeautifulSoup object from the .webpage file loaded.
    """
    f = open(filename, 'r')
    read_page = f.read()
    page_soup_xml = BeautifulSoup(read_page, 'lxml')
    return page_soup_xml