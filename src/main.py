from utils import Helper
from processor import Processor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('numexpr').setLevel(logging.WARNING)

HELPER = Helper()
PROCESSOR = Processor()

def process():
    try:
        category = HELPER.read_from_json('config/config_sheet.json')
        for item in category:
            logging.info(f'Processing {item["sheet_id"]}')
            new_run(item)
            rerun(item)
            items = HELPER.sanitize(f"output/{item['output']}")
            HELPER.to_google_sheet(items, sheet_name=item["sheet_name"], sheet_url=item["sheet_url"])
    except Exception as e:
        logging.error(f'Error in process: {e}')

def new_run(item):
    try:
        HELPER = Helper()
        HELPER.write_to_json([], f"output/{item['output']}")
        HELPER.write_to_json([], f"output/{item['failed_scraped']}")
        PROCESSOR.process(item)
    except Exception as e:
        logging.error(f'Error in new_run: {e}')

# rerun failed config
def rerun(item):
    try:
        logging.info(f'Rerunning failed config')
        failed_config = HELPER.read_from_json(f"output/{item['failed_scraped']}")
        PROCESSOR.process(item, failed_config)
    except Exception as e:
        logging.error(f'Error in rerun: {e}')
       
# trigger rerun 
def trig_rerun():
    try:
        category = HELPER.read_from_json('config/config_sheet.json')
        for item in category:
            HELPER.write_to_json([], f"output/{item['failed_scraped']}")
            rerun(item)
    except Exception as e:
        logging.error(f'Error in process: {e}')

if __name__ == '__main__':
    process()
    
    # rerun failed config
    trig_rerun()
    