from apartment import Apartment
from logging import Logger

import json
import requests
import re

def get_equity_apartments(url: str, property_name:str, property_address: str, logger: Logger) -> list:
  headers = {"User-Agent": ""}
  response = requests.get(url, headers=headers)
  if response is None:
    logger.error(f"Could not get {property_name} apartments, response is None.")
    return None

  availability_regex = re.compile("(?<=ea5.unitAvailability = )\{.*\}(?=;)")
  availability_string = availability_regex.search(response.text).group()
  availability_json = json.loads(availability_string)
  bedroom_types = availability_json["BedroomTypes"]

  apartments = []

  for bedroom_type in bedroom_types:
    for unit in bedroom_type["AvailableUnits"]:
      for term in unit["Terms"]:
        apartment = Apartment()
        apartment.property_name = property_name
        apartment.property_address = property_address
        apartment.pricing = term["Price"]
        apartment.lease_term = term["Length"]
        apartment.beds = unit["Bed"]
        apartment.baths = unit["Bath"]
        apartment.size = unit["SqFt"]
        apartment.building = unit["BuildingId"]
        apartment.unit = unit["UnitId"]
        apartment.availability_date = unit["AvailableDate"]

        if unit["Floor"].split(" ")[1].isnumeric():
          apartment.floor = unit["Floor"].split(" ")[1]
        else:
          apartment.floor = apartment.unit[0]

        apartments.append(apartment)
  
  return apartments
