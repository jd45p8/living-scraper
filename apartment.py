class Apartment():
  def __init__(self) -> None:
    self.property_name = None
    self.lease_term = None
    self.pricing = None
    self.beds = None
    self.baths = None
    self.size = None
    self.building = None
    self.floor = None
    self.unit = None
    self.availability_date = None
    self.property_address =  None
  
  @staticmethod
  def get_headder() -> str:
    string = ""
    string += "Property Name; "
    string += "Lease Term; "
    string += "Pricing; "
    string += "Bedromms; "
    string += "Bathrooms; "
    string += "Size; "
    string += "Building; "
    string += "Floor; "
    string += "Unit; "
    string += "Availability Date; "
    string += "Property Address"
    return string
  
  def __repr__(self) -> str:
    string = ""
    string += f"Property Name: {self.property_name}; "
    string += f"Lease Term: {self.lease_term}; "
    string += f"Pricing: {self.pricing}; "
    string += f"Bedromms: {self.beds}; "
    string += f"Bathrooms: {self.baths}; "
    string += f"Size: {self.size}; "
    string += f"Building: {self.building}; "
    string += f"Floor: {self.floor}; "
    string += f"Unit: {self.unit}; "
    string += f"Availability Date: {self.availability_date}; "
    string += f"Property Address: {self.property_address}"
    return string
  
  def __str__(self) -> str:
    string = ""
    string += f"{self.property_name}; "
    string += f"{self.lease_term}; "
    string += f"{self.pricing}; "
    string += f"{self.beds}; "
    string += f"{self.baths}; "
    string += f"{self.size}; "
    string += f"{self.building}; "
    string += f"{self.floor}; "
    string += f"{self.unit}; "
    string += f"{self.availability_date}; "
    string += f"{self.property_address}"
    return string