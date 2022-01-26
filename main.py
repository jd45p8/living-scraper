import logging
import json

from os import path
from tqdm import tqdm
from apartment import Apartment
from scrapers.equity_apartments import get_equity_apartments
from scrapers.sight_map import get_sight_map_apartments
from scrapers.udr import get_udr_apartments

if __name__ == "__main__":
  import os

  if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

  logger = logging.getLogger(__name__)
  logger.setLevel(logging.DEBUG)

  streamHandler = logging.StreamHandler()
  streamHandler.setLevel(logging.DEBUG)

  formatter = logging.Formatter("%(levelname)s - %(name)s - %(asctime)s -> %(message)s")

  streamHandler.setFormatter(formatter)

  logger.addHandler(streamHandler)

  PROPERTIES_FILE = os.getenv("PROPERTIES_FILE")
  if PROPERTIES_FILE is None:
    PROPERTIES_FILE = "properties.json"
  
  if not path.isfile(PROPERTIES_FILE):
    logger.error(f"File {PROPERTIES_FILE} not found.")
    exit()

  properties_file = open(PROPERTIES_FILE)
  try:
    properties = json.load(properties_file)
  except json.decoder.JSONDecodeError:
    properties_file.close()
    logger.error(f"Could not decode {PROPERTIES_FILE} JSON file.")
    exit()
  properties_file.close()
  
  if not properties or type(properties) is not list:
    logger.warning("No properties found.")
    exit()
  
  apartments = []
  for property in tqdm(properties):
    apartments_url = property["url"]
    property_name = property["name"]
    property_address = property["address"]
    scraper = property["scraper"]
    new_apartments = []

    if scraper == "equity_apartments":
      new_apartments = get_equity_apartments(apartments_url, property_name, property_address, logger)
    elif scraper == "sight_map":
      new_apartments = get_sight_map_apartments(apartments_url, property_name, property_address, logger)
    elif scraper == "udr":
      pricing_url = property["pricing_url"]
      new_apartments = get_udr_apartments(apartments_url, pricing_url, property_name, property_address, logger)
    else:
      logger.warning(f"Scraper {scraper} not found for {property_name}.")

    if new_apartments is not None:
      apartments.extend(new_apartments)
  
  apartments.sort(key=lambda a: a.pricing)

  OUTPUT_FILE = os.getenv("OUTPUT_FILE")
  if OUTPUT_FILE is None:
    OUTPUT_FILE = "output.json"
  
  with open(OUTPUT_FILE, "w") as output_file:
    output_file.write(f"{Apartment.get_headder()}\n")
    for apartment in apartments:
      output_file.write(f"{apartment}\n")