import pandas as pd
from pathlib import Path

from classes.pavilion import Pavilion
from classes.intersection import Intersection


class DataManager:

    def __init__(self):
        base_path = Path(__file__).resolve().parent.parent
        data_path = base_path / "data"

        self.locations = pd.read_csv(data_path / "location.csv")
        self.connections = pd.read_csv(data_path / "connections.csv")
        self.crowd_data = pd.read_csv(data_path / "crowd_data.csv")

        self.pavilions = []
        self.intersections = []

    def create_pavilions(self):
        pavilion_data = (
            self.locations
            .dropna(subset=["pavilion_id"])
            .drop_duplicates(subset=["pavilion_id"])
        )

        for _, row in pavilion_data.iterrows():
            pavilion = Pavilion(
                pavilion_id=row["pavilion_id"],
                country=row["country"],
                location=row["pavilion_name"],
                has_ar=False
            )

            self.pavilions.append(pavilion)

        return self.pavilions

    def create_intersections(self):
        connections_map = {}

        for _, row in self.connections.iterrows():
            source = row["from_location"]
            destination = row["to_location"]

            connections_map.setdefault(source, []).append(destination)
            connections_map.setdefault(destination, []).append(source)

        for location_id, connected_locations in connections_map.items():
            if len(connected_locations) >= 3:
                location_row = self.locations[
                    self.locations["location_id"] == location_id
                ]

                if location_row.empty:
                    continue

                location_name = location_row.iloc[0]["location_name"]

                intersection = Intersection(
                    intersection_id=location_id,
                    location=location_name,
                    connected_locations=connected_locations
                )

                self.intersections.append(intersection)

        return self.intersections

    def get_pavilions(self):
        return self.pavilions

    def get_intersections(self):
        return self.intersections