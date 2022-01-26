from apartment import Apartment
from copy import deepcopy
from logging import Logger

import requests

import json

def get_sight_map_apartments(url: str, property_name:str, property_address: str, logger: Logger) -> list:
  headers = {"User-Agent": ""}
  response = requests.get(url, headers=headers)
  if response is None:
    logger.error(f"Could not get {property_name} apartments, response is None.")
    return None

  response_json = json.loads(response.text)
  units = response_json["data"]["units"]
  floor_plans = {item["id"]: item for item in response_json["data"]["floor_plans"]}
  floors = {item["id"]: item for item in response_json["data"]["floors"]}

  apartments = []

  for unit in units:
    apartment = Apartment()
    apartment.property_name = property_name
    apartment.property_address = property_address
    apartment.pricing = unit["price"]
    apartment.size = unit["area"]
    apartment.unit = unit["unit_number"]

    if unit["display_lease_term"]:
      apartment.lease_term = unit["display_lease_term"].split(" ")[0]
    
    date = unit["available_on"].split("-")
    apartment.availability_date = f"{int(date[1])}/{int(date[2])}/{date[0]}"

    floor_plan = floor_plans[unit["floor_plan_id"]]
    apartment.beds = floor_plan["bedroom_count"]
    apartment.baths = floor_plan["bathroom_count"]

    floor = floors[unit["floor_id"]]
    apartment.floor = floor["filter_short_label"]

    if unit["leasing_price_url"]:
      leasing_price_reponse = requests.get(unit["leasing_price_url"], headers=headers)
      
      if leasing_price_reponse is None:
        logger.error(f"Could not get {property_name} apartments pricing, response is None.")
      else:
        leasing_prices = json.loads(leasing_price_reponse.text)
        if leasing_prices["data"]["options"]:
          for leasing_price in leasing_prices["data"]["options"]:
            apartment = deepcopy(apartment)
            apartment.lease_term = leasing_price["lease_term"]
            apartment.pricing = leasing_price["display_price"]
            apartment.pricing = apartment.pricing.replace("$", "")
            apartment.pricing = apartment.pricing.replace(",", "")
            apartment.pricing = int(apartment.pricing)
            apartments.append(apartment)
        
          continue

    apartments.append(apartment)
  
  return apartments
