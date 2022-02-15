from cmath import log
from copy import deepcopy
from logging import Logger
from bs4 import BeautifulSoup
from datetime import datetime

import requests
import json
import re

from apartment import Apartment

def get_rent_cafe_apartments(url: str, pricing_url: str, property_name:str, property_address: str, logger: Logger) -> list:
  headers = {"User-Agent": ""}
  response = requests.get(url, headers=headers)
  if response is None:
    logger.error(f"Could not get {property_name} apartments, response is None.")
    return None
  
  soup = BeautifulSoup(response.text, "html.parser")
  floor_plans_headers = soup.select("#hideMap > #innerformdiv > .row-fluid > .block > .row-fluid")
  floor_plans_tables = soup.select("#hideMap > #innerformdiv > .row-fluid > .block > table")

  beds_regex = re.compile("\d+(?= Bedroom)")
  baths_regex = re.compile("\d+(?= Bathroom)")
  pricing_options_regex = re.compile("(?<=var PricingData = )[\w\s\n\t\"\:\,\ \.\[\]\{\}\/]+(?=;)")
  pricing_url_params_regex = re.compile("(?<=\'rentaloptions.aspx\?).+(?=\')")
  move_in_date_regex = re.compile("(?<=MoveInDate=)\d{1,2}\/\d{1,2}\/\d{4}")
  
  apartments = []

  for floor_plan_header, floor_plan_table in zip(floor_plans_headers, floor_plans_tables):
    floor_plan_name = floor_plan_header.find(id="other-floorplans").text
    beds = beds_regex.search(floor_plan_name).group()
    baths = baths_regex.search(floor_plan_name).group()
    
    units = floor_plan_table.select("tbody > tr")
    for unit in units:
      apartment = Apartment()
      apartment.property_name = property_name
      apartment.property_address =  property_address
      apartment.beds = beds
      apartment.baths = baths

      apartment.size = unit.find(attrs={"data-label": "Sq. Ft."}).text
      apartment.unit = unit.find(class_="UnitSelect").attrs["id"]
      apartment.floor = apartment.unit[0]

      apartment.pricing = unit.find(attrs={"data-label": "Rent"}).text.split("-")[0]
      apartment.pricing = apartment.pricing.replace("$", "")
      apartment.pricing = apartment.pricing.replace(",", "")
      if not apartment.pricing.isnumeric():
        logger.warning(f"Pricing is {apartment.pricing} for unit {apartment.unit} on {property_name}.")
        continue
      
      apartment.pricing = int(apartment.pricing)

      on_click = unit.find(class_="UnitSelect").attrs["onclick"]
      pricing_url_params = pricing_url_params_regex.search(on_click).group()
      
      availability_date = unit.find(attrs={"data-label": "Date Available"})
      if availability_date and availability_date.text == "Available":
        date = datetime.now()
        apartment.availability_date = f"{date.month}/{date.day}/{date.year}"
      else:
        apartment.availability_date = move_in_date_regex.search(pricing_url_params).group()

      pricing_response = requests.get(f"{pricing_url}?{pricing_url_params}")
      if pricing_response is None:
        logger.error(f"Could not get {property_name} apartments pricing, response is None.")

      pricing_options_string = pricing_options_regex.search(pricing_response.text).group()
      pricing_options = json.loads(pricing_options_string)

      first_key = list(pricing_options)[0]
      if not first_key.isnumeric():
        pricing_options = pricing_options[first_key]
      
      for lease_term, value in pricing_options.items():
        if not lease_term.isnumeric():
          continue

        apartment = deepcopy(apartment)
        apartment.lease_term =  lease_term
        apartment.pricing = value["price"]
      
        apartments.append(apartment)
  
  return apartments