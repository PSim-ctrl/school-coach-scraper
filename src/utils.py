from asyncioReq import AsyncRequester
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('numexpr').setLevel(logging.WARNING)

class Helper():
    def __init__(self):
        pass
    
    def to_google_sheet(self, data, sheet_name=None, sheet_url=None):
        try:
            creds_file = "config/cred.json"  # Replace with your credentials file

            sheet = self.setup_google_sheet(creds_file, sheet_url, sheet_name)
        
            self.write_to_google_sheet(sheet, data)
            # self.write_to_json(data, f"output/{filtered_output}")
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def setup_google_sheet(creds_file, shared_sheet_url, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        # Open the sheet by URL
        spreadsheet = client.open_by_url(shared_sheet_url)
        if sheet_name:
            sheet = spreadsheet.worksheet(sheet_name)
        else:
            sheet = spreadsheet.sheet1
        return sheet

    # Write data to Google Sheets
    @staticmethod
    def write_to_google_sheet(sheet, data):
        sheet.clear()  # Clear existing data
        if data:
            # Write headers
            headers = list(data[0].keys())
            sheet.insert_row(headers, 1)
            # Prepare data rows
            rows = [list(row.values()) for row in data]
            # Batch update rows
            sheet.insert_rows(rows, 2)
        print("Data written to Google Sheet")
        
    def get_data_from_google_sheet(self, sheet_name=None, sheet_url=None):
        try:
            creds_file = "config/cred.json"  # Replace with your credentials file
            sheet = self.setup_google_sheet(creds_file, sheet_url, sheet_name)
            data = sheet.get_all_records()
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None

    def write_to_json(self, data, filename):
        '''
        write output data to a json file.
        '''
        try:
            with open(filename, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            logging.error(f'Error in write_to_json: {e}')
        
    def read_from_json(self, filename):
        '''
        read data from a json file.
        this could also use to transform data without scraping website all over again.
        '''
        try:
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            logging.error(f'Error in read_from_json: {e}')
            return None

    def sanitize(self, filename):
        try:
            json_items = self.read_from_json(filename)
            items = self.remove_duplicates(json_items)
            exclude = ['trainer', 'operation', 'operations', 'equipment', 'strength', 'conditioning', 'student', 'students', 'performance', 'volunteer', 'volunteers']
            _temp = []
            for item in items:
                item = {key: (value if value is not None else '') for key, value in item.items()}
                item['Last Name'] = re.sub(r"'\d{2}", "", item['Last Name'])
                if not any(exc_item in item['Title'].lower() for exc_item in exclude):
                    if "coach" in item['Title'].lower() or "entraîneur" in item['Title'].lower():
                         _temp.append(item)

            return _temp
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def remove_duplicates(self, data):
        seen = set()
        unique_data = []
        for item in data:
            item_tuple = tuple(item.items())
            if item_tuple not in seen:
                seen.add(item_tuple)
                unique_data.append(item)
        return unique_data

    # for debugging purposes
    def get_single_school(_processor, category_womens):
        items = []
        config_item = {
            "college/university": "University of Saskatchewan",
            "school name": "Saskatchewan Huskies",
            "website": "huskies.usask.ca",
            "urls": [
                {
                    "url": "https://huskies.usask.ca/sports/womens-ice-hockey/roster#sidearm-roster-coaches",
                    "category": "Women's U Sports Hockey Coaches",
                    "location": "Pennsylvania",
                    "conference": "MAC"
                },
                {
                    "url": "https://oraprdnt.uqtr.uquebec.ca/portail/gscw031?owa_no_site=133&owa_no_fiche=49&owa_bottin=",
                    "category":"Men's U Sports Hockey Coaches",
                    "location": "",
                    "conference": ""
                }
            ],
            "module": "parser.usask",
            "class": "Parser"
        }

        special = [
            "Lakehead University"
        ]

        urls = [url for url in config_item["urls"] if url["category"] in category_womens]
        for url in urls:
            print(f'Processing {config_item["school name"]}')
            _processor.get_module(config_item, url) # set module
            if config_item["college/university"] in special:
                raw_html = AsyncRequester.get(url["url"])
                raw_html = [raw_html, url["url"]]
                items.extend(_processor.get_items(raw_html))
            else:
                coaches_urls = _processor.get_coaches_urls(url)
                raw_html = AsyncRequester().run(coaches_urls)
                items.extend(_processor.multi_process(raw_html))
        print(items)
