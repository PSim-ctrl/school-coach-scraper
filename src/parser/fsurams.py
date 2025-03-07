import logging
from bs4 import BeautifulSoup
from requester import Requester

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser():
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference

    def process(self, raw_html, url):
        try:
            logging.debug(f"Processing URL: {url}")
            item = self.get_item(self.school, raw_html, url)
            return item
        except Exception as e:
            logging.error(f"Error processing URL {url}: {e}")
            return []

    def raw_html_to_soup(self, raw_html):
        return BeautifulSoup(raw_html, 'html.parser')

    def get_item(self, school, raw_html, url):
        _soup = self.raw_html_to_soup(raw_html)
        item = {}
        item['First Name'], item['Last Name'] = self.get_name(_soup)
        item['Title'] = self.get_title(_soup)
        item['School'] = school
        item['Email'] = self.get_email(_soup)
        item['Phone'] = self.get_number(_soup)
        item['Image URL'] = self.image_url(_soup)
        item['Profile URL'] = url
        item['Category'] = self.category
        item['Location'] = self.location
        item['Conference'] = self.conference

        logging.debug(f"Item extracted: {item}")
        return item

    def get_coaches_url(self, *args, **kwargs):
        try:
            soup = self.raw_html_to_soup(kwargs['raw_data'])
            urls = []
            parent_tag = soup.select_one('.coaches-headshot-container')
            if parent_tag:
                tags = parent_tag.select('h5 a')
                urls = [f"{self.base_url}{tag.get('href')}" for tag in tags]
            logging.debug(f"Coaches URLs extracted: {urls}")
            return urls
        except Exception as e:
            logging.error(f"Error getting coaches URLs: {e}")
            return None

    def get_name(self, soup):
        try:
            f_name = None
            l_name = None
            tag = soup.select_one('.name')
            if tag:
                name = tag.get_text().strip().split(' ')
                name = [item for item in name if item]  # Cleanse or remove empty strings
                f_name = name[0]
                l_name = name[1]
            logging.debug(f"Name extracted: {f_name} {l_name}")
            return f_name, l_name
        except Exception as e:
            logging.error(f"Error getting name: {e}")
            return None, None

    def get_title(self, soup):
        try:
            title = None
            tag = soup.find(lambda tag: tag.name == "dt" and "Title" in tag.text)
            if tag:
                next_tag = tag.find_next('dd')
                title = next_tag.get_text().strip()
            logging.debug(f"Title extracted: {title}")
            return title
        except Exception as e:
            logging.error(f"Error getting title: {e}")
            return None

    def get_email(self, soup):
        try:
            email = None
            tag = soup.find(lambda tag: tag.name == "dt" and "Email" in tag.text)
            if tag:
                next_tag = tag.find_next('dd')
                email = next_tag.get_text().strip()
            logging.debug(f"Email extracted: {email}")
            return email
        except Exception as e:
            logging.error(f"Error getting email: {e}")
            return None

    def get_number(self, soup):
        try:
            number = None
            tag = soup.find(lambda tag: tag.name == "dt" and "Phone" in tag.text)
            if tag:
                next_tag = tag.find_next('dd')
                number = next_tag.get_text().strip()
            logging.debug(f"Phone number extracted: {number}")
            return number
        except Exception as e:
            logging.error(f"Error getting phone number: {e}")
            return None

    def image_url(self, soup):
        try:
            image_url = ""
            tag = soup.select_one('.player-headshot img')
            if tag:
                image_url = f"{self.base_url}{tag.get('src')}"
                logging.debug(f"Image URL extracted: {image_url}")
            return image_url
        except Exception as e:
            logging.error(f"Error getting image URL: {e}")
            return None