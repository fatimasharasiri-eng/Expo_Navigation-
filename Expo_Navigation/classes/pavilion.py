class Pavilion:

    def __init__(self, pavilion_id, country, location, has_ar):
        self.pavilion_id = pavilion_id
        self.country = country
        self.location = location
        self.has_ar = has_ar

    def display_info(self):
        print(f"Pavilion ID: {self.pavilion_id}")
        print(f"Country: {self.country}")
        print(f"Location: {self.location}")
        print(f"Has AR: {self.has_ar}")