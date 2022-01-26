from copy import deepcopy
from apartment import Apartment
from logging import Logger
from datetime import datetime, timezone

import json
import requests
import re

def get_udr_apartments(url: str, pricing_url: str, property_name:str, property_address: str, logger: Logger) -> list:
  headers = {"User-Agent": ""}
  response = requests.get(url, headers=headers)
  if response is None:
    logger.error(f"Could not get {property_name} apartments, response is None.")
    return None

  availability_regex = re.compile("(?<=window.udr.jsonObjPropertyViewModel = )\{.*\}(?=;)")
  availability_string = availability_regex.search(response.text).group()
  availability_json = json.loads(availability_string)  
  floor_plans = availability_json["floorPlans"]

  date_regex = re.compile("(?<=/Date\()\d+(?=\)/)")

  apartments = []

  for floor_plan in floor_plans:
    units = floor_plan["units"]
    for unit in units:
      apartment = Apartment()
      apartment.property_name = property_name
      apartment.property_address = property_address
      apartment.pricing = unit["rentMax"]
      apartment.beds = floor_plan["bedRooms"]
      apartment.baths = floor_plan["bathRooms"]
      apartment.size = unit["sqFt"]
      apartment.building = unit["building"]
      apartment.floor = unit["floorNumber"]
      apartment.unit = unit["unitName"]
      
      unix_availability_date = date_regex.search(unit["availableDate"]).group()
      unix_availability_date = int(unix_availability_date)/1000
      date = datetime.fromtimestamp(unix_availability_date, timezone.utc)
      apartment.availability_date = f"{date.month}/{date.day}/{date.year}"

      rent_matrix_response = requests.get(f"{pricing_url}/{unit['ilsUnitId']}/rentmatrix")
      if rent_matrix_response is None:
        logger.error(f"Could not get {property_name} apartments pricing, response is None.")

      rent_matrix = json.loads(rent_matrix_response.text)
      if rent_matrix:
        for rent in rent_matrix:
          if rent["MoveInDate"] == unit["availableDate"]:
            apartment = deepcopy(apartment)
            apartment.lease_term = rent["LeaseTerm"]
            apartment.pricing = rent["Rent"]
            apartments.append(apartment)
              
        continue

      apartments.append(apartment)
  
  return apartments
