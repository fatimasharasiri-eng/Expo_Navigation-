
import random
import pandas as pd
from pathlib import Path


LOW_LIMIT = 40
HIGH_LIMIT = 75


class Corridor:

    def __init__(
        self,
        corridor_id,
        start_point,
        end_point,
        distance,
        capacity,
        people_count=0
    ):
        self.corridor_id = corridor_id
        self.start_point = start_point
        self.end_point = end_point
        self.distance = distance
        self.capacity = capacity
        self.people_count = people_count

    def calculate_occupancy(self):

        if self.capacity <= 0:
            return 0

        occupancy = (self.people_count / self.capacity) * 100

        return round(occupancy, 2)

    def get_crowd_level(self):

        occupancy = self.calculate_occupancy()

        if occupancy < LOW_LIMIT:
            return "Low"

        elif occupancy < HIGH_LIMIT:
            return "Medium"

        return "High"

    def update_crowd(self, people_count):

        self.people_count = max(
            0,
            min(people_count, self.capacity)
        )


class CrowdManager:

    SCENARIOS = {
        "Quiet Day": (10, 35),
        "Normal Day": (35, 65),
        "Busy Day": (65, 90)
    }

    def __init__(self, seed=None):

        self.random = random.Random(seed)

        base_path = Path(__file__).resolve().parent.parent
        data_path = base_path / "data"

        self.locations = pd.read_csv(
            data_path / "location.csv"
        )

        self.connections = pd.read_csv(
            data_path / "connections.csv"
        )

        self.corridors = {}

        self.build_corridors()

        self.set_crowd_scenario("Normal Day")

    def build_corridors(self):

        for index, row in self.connections.iterrows():

            start_point = row["from_location"]
            end_point = row["to_location"]

            distance = float(row["distance_m"])

            start_location = self.locations[
                self.locations["location_id"] == start_point
            ]

            end_location = self.locations[
                self.locations["location_id"] == end_point
            ]

            if start_location.empty or end_location.empty:
                continue

            capacity = min(
                float(start_location.iloc[0]["capacity"]),
                float(end_location.iloc[0]["capacity"])
            )

            corridor_id = f"C{index + 1}"

            self.corridors[corridor_id] = Corridor(
                corridor_id=corridor_id,
                start_point=start_point,
                end_point=end_point,
                distance=distance,
                capacity=capacity
            )

    def set_crowd_scenario(self, scenario="Normal Day"):

        min_rate, max_rate = self.SCENARIOS.get(
            scenario,
            self.SCENARIOS["Normal Day"]
        )

        for corridor in self.corridors.values():

            occupancy_rate = self.random.uniform(
                min_rate,
                max_rate
            )

            people_count = int(
                corridor.capacity * occupancy_rate / 100
            )

            corridor.update_crowd(people_count)

    def update_crowd(self):

        for corridor in self.corridors.values():

            change = self.random.randint(-10, 10)

            new_count = corridor.people_count + change

            corridor.update_crowd(new_count)

    def simulate_crowd_change(self):

        self.update_crowd()

    def get_corridor(self, start_point, end_point):

        for corridor in self.corridors.values():

            if (
                corridor.start_point == start_point
                and corridor.end_point == end_point
            ) or (
                corridor.start_point == end_point
                and corridor.end_point == start_point
            ):

                return corridor

        return None

    def get_crowd_rate(self, start_point, end_point):

        corridor = self.get_corridor(
            start_point,
            end_point
        )

        if corridor is None:
            return 0

        return corridor.calculate_occupancy() / 100

    def get_crowd_level(self, start_point, end_point):

        corridor = self.get_corridor(
            start_point,
            end_point
        )

        if corridor is None:
            return "Unknown"

        return corridor.get_crowd_level()
