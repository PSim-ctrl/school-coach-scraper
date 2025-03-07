import multiprocessing
import json
import importlib
import logging
from utils import Helper
from asyncioReq import AsyncRequester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('numexpr').setLevel(logging.WARNING)

class Processor:
    def __init__(self):
        self.module = None
    
    def multi_process(self, raw_htmls):
        try:
            with multiprocessing.Pool(processes=len(raw_htmls)) as pool:
                results = pool.map(self.get_items, raw_htmls)
            return results
        except Exception as e:
            logging.error(f'Error in multi_process: {e}')
            return None

    def process(self, school_sports_category, rerun=None):
        try:
            _helper = Helper()
            with open("config/config.json", "r") as f:
                config = json.load(f)
                
            special = [
                "Lakehead University"
            ]
            
            if rerun:
                config = rerun
                
            for config_item in config:
                urls = [url for url in config_item["urls"] if url["category"] in school_sports_category["category"]]
                for url in urls:
                    logging.info(f'Processing {config_item["school name"]}')
                    self.get_module(config_item, url) # set module
                    if config_item["college/university"] in special:
                        self.process_special(url, _helper, config_item, school_sports_category)
                    else:
                        self.process_regular(url, _helper, config_item, school_sports_category)
                            
        except Exception as e:
            logging.error(f'Error in process: {e}')
        
    def process_special(self, url, _helper, config_item, school_sports_category):
        try:
            items = _helper.read_from_json(f"output/{school_sports_category['output']}")
            failed = _helper.read_from_json(f"output/{school_sports_category['failed_scraped']}")
            raw_html = AsyncRequester.get(url["url"])
            raw_html = [raw_html, url["url"]]
                        
            data = self.get_items(raw_html)
            if data:
                items.append(data)
                _helper.write_to_json(items, f"output/{school_sports_category['output']}")
            else:
                logging.error(f'Error in get_items: {data}')
                failed.append(config_item)
                _helper.write_to_json(failed, f"output/{school_sports_category['failed_scraped']}")
        except Exception as e:
            logging.error(f'Error in process_special: {e}')
            _helper.save_failed_config(config_item)
        
    def process_regular(self, url, _helper, config_item, school_sports_category):
        try:
            items = _helper.read_from_json(f"output/{school_sports_category['output']}")
            failed = _helper.read_from_json(f"output/{school_sports_category['failed_scraped']}")
            coaches_urls = self.get_coaches_urls(url)
            raw_html = AsyncRequester().run(coaches_urls)
            data = self.multi_process(raw_html)
            if data:
                items.extend(data)
                _helper.write_to_json(items, f"output/{school_sports_category['output']}")
            else:
                logging.error(f'Error in get_items: {data}')
                failed.append(config_item)
                _helper.write_to_json(failed, f"output/{school_sports_category['failed_scraped']}")
        except Exception as e:
            logging.error(f'Error in process_regular: {e}')
            _helper.save_failed_config(config_item)
        
    def get_coaches_urls(self, url):
        try:
            raw_data = AsyncRequester.get(url["url"])
            coaches_urls = self.module.get_coaches_url(raw_data=raw_data, url=url['url'])
            return coaches_urls
        except Exception as e:
            logging.error(f'Error in get_coaches_urls: {e}')
            return None
        
    def get_items(self, raw_data):
        try:
            item = self.module.process(raw_data[0], raw_data[1])
            return item
        except Exception as e:
            logging.error(f'Error in get_items: {e}')
            return None
        
    def get_module(self, config_item, url):
        try:
            module = importlib.import_module(config_item["module"])
            ATTR = getattr(module, config_item["class"])
            school = config_item["college/university"]
            base_url = f'https://{config_item["website"]}'
            category = url["category"]
            location = url["location"]
            conference = url["conference"]
            parser = ATTR(school, base_url, category, location, conference)
            self.module = parser
        except Exception as e:
            logging.error(f'Error in get_module: {e}')