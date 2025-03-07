import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from requester import Requester
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser:
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference
        logging.info(f'Initialized Parser for {school}')

    def process(self, raw_html, url):
        try:
            logging.info(f'Processing URL: {url}')
            item = self.get_item(self.school, raw_html, url)
            return item
        except Exception as e:
            logging.error(f'Error processing URL: {url} - {e}')
            return []

    def raw_html_to_soup(self, raw_html):
        return BeautifulSoup(raw_html, 'html.parser')

    def get_item(self, school, raw_html, url):
        logging.info(f'Getting item for URL: {url}')
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

        return item

    def get_name(self, soup):
        try:
            f_name = None
            l_name = None
            tag = soup.select_one('.entraineur-prenom-nom-detail')
            if tag:
                name = tag.get_text().strip().split(' ')
                name = [item for item in name if item]  # Cleanse or remove empty strings
                f_name = name[0]
                l_name = name[1]
            return f_name, l_name
        except Exception as e:
            logging.error(f'Error getting name: {e}')
            return None, None

    def get_title(self, soup):
        try:
            title = None
            tag = soup.select_one('.entraineur-poste-detail')
            if tag:
                title = tag.get_text().strip()
            return title
        except Exception as e:
            logging.error(f'Error getting title: {e}')
            return None

    def get_email(self, soup):
        try:
            email = None
            tag = soup.select_one('.courriel.Courrielinvisible')
            if tag:
                email = tag.get_text().strip()
            return email
        except Exception as e:
            logging.error(f'Error getting email: {e}')
            return None

    def get_number(self, soup):
        try:
            number = None
            tag = soup.select_one('.telephone.Téléphoneinvisible')
            if tag:
                number = tag.get_text().strip()
            return number
        except Exception as e:
            logging.error(f'Error getting number: {e}')
            return None

    def image_url(self, soup):
        try:
            image_url = ""
            tag = soup.select_one('.entraineur-photo-detail img')
            if tag:
                image_url = tag.get('src')
            return image_url
        except Exception as e:
            logging.error(f'Error getting image URL: {e}')
            return None

    def get_driver(self):
        logging.info('Setting up WebDriver')
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-unsafe-swiftshader")

        # Set up the WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    def get_coaches_url(self, *args, **kwargs):
        urls = []
        driver = self.get_driver()

        logging.info(f'Fetching coaches URLs from: {kwargs["url"]}')
        driver.get(kwargs['url'])

        # Add explicit wait
        wait = WebDriverWait(driver, 60)
        links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.entraineur')))
        for link in links:
            _href = link.get_attribute('href')
            match = re.search(r'afficherDetailFormReponse\(\d+, (\d+),', _href)
            url = f"https://oraprdnt.uqtr.uquebec.ca/portail/gscw045a.afficher_detail_form_reponse?owa_no_site=133&owa_bottin=&owa_no_fiche=49&owa_no_form_reponse={match.group(1)}"
            urls.append(url)

        driver.quit()
        logging.info(f'Found {len(urls)} coach URLs')
        return urls