import json

from . import country_codes

class Hotel:
    def __init__(self):
        self.corresponding_jsons = []

        self.id = None
        self.destination_id = None

        self.name = None
        self.latitude = None
        self.longitude = None
        self.address = None
        self.city = None
        self.country = None
        self.description = None
        self.room_amenities = []
        self.general_amenities = []
        self.room_images = []    
        self.site_images = []    
        self.amenity_images = [] 
        self.booking_conditions = []

    
    def __parse_name_data(self):
        names_dict = {} # Dictionary to count the occurences

        possible_name_strings = ["name", "hotel_name", "Name"]
        for current_json in self.corresponding_jsons:
            for str in possible_name_strings:
                if str in current_json:
                    hotel_name = current_json[str]
                    if hotel_name in names_dict:
                        names_dict[hotel_name] += 1
                    else:
                        names_dict[hotel_name] = 0

        # Choose the name with the most occurences,
        # I guess thats the one most likely to be correct
        best_name = max(names_dict, key=lambda k: names_dict[k])
        self.name = best_name

    def __parse_latlon_data(self):
        for current_json in self.corresponding_jsons:
            if self.latitude == None:
                lat = None
                if "lat" in current_json and (isinstance(current_json["lat"], float)):
                    lat = current_json["lat"]
                elif "Latitude" in current_json and (isinstance(current_json["Latitude"], float)):
                    lat = current_json["Latitude"]

                if lat is not None and lat >= -90 and lat <= 90: # Check if in valid range
                    self.latitude = lat

            if self.longitude == None:
                lon = None
                if "lng" in current_json and (isinstance(current_json["lng"], float)):
                    lon = current_json["lng"]
                elif "Longitude" in current_json and (isinstance(current_json["Longitude"], float)):
                    lon = current_json["Longitude"]

                if lon is not None and lon >= -180 and lon <= 180: # Check if in valid range
                    self.longitude = lon

    def __parse_address_data(self):
        address_candidate = ""
        for current_json in self.corresponding_jsons:

            if self.city is None and "City" in current_json and current_json["City"] is not None:
                self.city = current_json["City"]

            # Remove whitespace from start and end
            # Select the longest address, its probably more accurate
            
            address = ""
            if "address" in current_json and current_json["address"] is not None:
                address = current_json["address"].strip() 
            elif "Address" in current_json and current_json["Address"] is not None:
                address = current_json["Address"].strip()
            elif "location" in current_json and "address" in current_json["location"] and current_json["location"]["address"] is not None:
                address = current_json["location"]["address"].strip()
            
            if "PostalCode" in current_json and current_json["PostalCode"] is not None:
                if not current_json["PostalCode"] in address:
                    address += ", " + current_json["PostalCode"]

            if len(address) > len(address_candidate):
                address_candidate = address
            

        if address_candidate != "":
            self.address = address_candidate

    def __parse_country_data(self):
        for current_json in self.corresponding_jsons:

            if "Country" in current_json:
                country_candidate = current_json["Country"]
                if country_candidate is None:
                    continue

                # If its a 2 letter code, parse it from the prepared list
                if len(country_candidate) == 2:
                    country_candidate = country_codes.get_country_name_from_code(country_candidate)
                    if len(country_candidate) != 0:
                        self.country = country_candidate
                        return
            elif "location" in current_json and "country" in current_json["location"]:
                if current_json["location"]["country"] is not None:
                    self.country = current_json["location"]["country"]
                    return
            
    def __parse_description_data(self):
        for current_json in self.corresponding_jsons:

            description_candidate = ""
            if "Description" in current_json:
                description_candidate = current_json["Description"]
            elif "details" in current_json:
                description_candidate = current_json["details"]
            elif "info" in current_json:
                description_candidate = current_json["info"]

            if description_candidate is None or description_candidate == "":
                continue

            description_candidate.strip()

            if self.description is None:
                self.description = description_candidate
            elif len(description_candidate) > len(self.description):  # The longer one is probably better
                self.description = description_candidate

    def __parse_amenities(self):
        for current_json in self.corresponding_jsons:
            if "Facilities" in current_json and current_json["Facilities"] is not None:
                for fac in current_json["Facilities"]:
                    if fac.lower() not in self.general_amenities:
                        self.general_amenities.append(fac.lower().strip())
            elif "amenities" in current_json and current_json["amenities"] is not None:
                if isinstance(current_json["amenities"], list):
                    for amen in current_json["amenities"]:
                        if amen.lower() not in self.room_amenities:
                            self.room_amenities.append(amen.lower().strip())
                else:
                    for s in current_json["amenities"]["general"]:
                        if s.lower() not in self.general_amenities:
                            self.general_amenities.append(s.lower().strip())
                    for s in current_json["amenities"]["room"]:
                        if s.lower() not in self.room_amenities:
                            self.room_amenities.append(s.lower().strip())

    def __read_image_data(self, item, container):
        dt = {}

        if "url" in item:

            # Check if its unique
            for c in container:
                if c["link"] == item["url"]:   
                    return

            dt["link"] = item["url"]
        elif "link" in item:

            # Check if its unique
            for c in container:
                if c["link"] == item["link"]:
                    return

            dt["link"] = item["link"]

        if "description" in item:
            dt["description"] = item["description"]
        elif "caption" in item:
            dt["description"] = item["caption"]

        container.append(dt)
 
    def __parse_images(self):
        for current_json in self.corresponding_jsons:
            if "images" not in current_json:
                continue

            if "rooms" in current_json["images"] and current_json["images"]["rooms"] is not None:
                for item in current_json["images"]["rooms"]:
                    self.__read_image_data(item, self.room_images)
            if "site" in current_json["images"] and current_json["images"]["site"] is not None:
                for item in current_json["images"]["site"]:
                    self.__read_image_data(item, self.site_images)
            if "amenities" in current_json["images"] and current_json["images"]["amenities"] is not None:
                for item in current_json["images"]["amenities"]:
                    self.__read_image_data(item, self.amenity_images)
            

    def __parse_booking_conditions(self):
        for current_json in self.corresponding_jsons:
            if "booking_conditions" in current_json and current_json["booking_conditions"] is not None:
                for condition in current_json["booking_conditions"]:
                    if condition == "":
                        continue

                    self.booking_conditions.append(condition.strip())

    # Fill the members from the previously collected JSON data
    def read_json_data(self):
        self.__parse_name_data()
        self.__parse_latlon_data()
        self.__parse_address_data()
        self.__parse_country_data()
        self.__parse_description_data()
        self.__parse_amenities()
        self.__parse_images()
        self.__parse_booking_conditions()

    # Return a dict similar to that in the homework specification
    def to_json(self):
        jsonobj = {}
        jsonobj["id"] = self.id
        jsonobj["destination_id"] = self.destination_id
        jsonobj["name"] = self.name

        jsonobj["location"] = {}
        jsonobj["location"]["lat"] = self.latitude
        jsonobj["location"]["lng"] = self.longitude
        jsonobj["location"]["address"] = self.address
        jsonobj["location"]["city"] = self.city
        jsonobj["location"]["country"] = self.country

        jsonobj["description"] = self.description

        jsonobj["amenities"] = {}
        jsonobj["amenities"]["general"] = self.general_amenities
        jsonobj["amenities"]["room"] = self.room_amenities

        jsonobj["images"] = {}
        jsonobj["images"]["rooms"] = self.room_images
        jsonobj["images"]["site"] = self.site_images
        jsonobj["images"]["amenities"] = self.amenity_images

        jsonobj["booking_conditions"] = self.booking_conditions

        return jsonobj