class Intersection:


 def __init__(self, intersection_id, location, connected_locations=None):
    self.intersection_id = intersection_id
    self.location = location
    self.connected_locations = connected_locations or []

 def display_info(self):
    print(f"Intersection ID: {self.intersection_id}")
    print(f"Location: {self.location}")
    print(f"Connected Locations: {self.connected_locations}")

