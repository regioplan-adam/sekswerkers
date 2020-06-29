import datetime
import logging
from __app__.applicatie import main_scraper

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    # start scrapers
    main_scraper.main()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
