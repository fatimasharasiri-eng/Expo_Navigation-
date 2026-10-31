import networkx as nx
class RouteManager:

    def __init__(self, crowd_manager):
     self.crowd_manager = crowd_manager
     self.locations = crowd_manager.locations
     self.connections = crowd_manager.connections
     self.graph = nx.Graph()
     self.build_graph()
    def build_graph(self):
        self.graph.clear()

        for _, row in self.locations.iterrows():
            self.graph.add_node(
                row["location_id"],
                name=row["location_name"],
                location_type=row["location_type"],
                capacity=row["capacity"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"])
            )

        for _, row in self.connections.iterrows():
            source = row["from_location"]
            destination = row["to_location"]

            if source not in self.graph or destination not in self.graph:
                raise ValueError(
                    f"Unknown location: {source} or {destination}"
                )

            self.graph.add_edge(
                source,
                destination,
                distance=float(row["distance_m"])
            )

        self.update_route_costs()
        return self.graph

    def calculate_route_cost(self, source, destination):
        distance = self.graph[source][destination]["distance"]

        crowd_rate = self.crowd_manager.get_crowd_rate(
            source,
            destination
        )

        # Distance remains in meters.
        # Crowd increases the routing cost, not the actual distance.
        crowd_penalty = 3.0
        cost = distance * (1 + crowd_penalty * crowd_rate)

        return cost

    def update_route_costs(self):
        for source, destination in self.graph.edges():
            self.graph[source][destination]["weight"] = (
                self.calculate_route_cost(source, destination)
            )

    def get_route_distance(self, route):
        total_distance = 0.0

        for source, destination in zip(route, route[1:]):
            total_distance += self.graph[source][destination]["distance"]

        return round(total_distance, 2)

    def find_route(self, start, destination):
        if start not in self.graph:
            raise ValueError(f"Start location not found: {start}")

        if destination not in self.graph:
            raise ValueError(
                f"Destination location not found: {destination}"
            )

        self.update_route_costs()

        try:
            # Recommended route: balances distance and crowd levels.
            recommended_route = nx.dijkstra_path(
                self.graph,
                source=start,
                target=destination,
                weight="weight"
            )

            recommended_cost = nx.dijkstra_path_length(
                self.graph,
                source=start,
                target=destination,
                weight="weight"
            )

            # Shortest route: ignores crowd and minimizes distance only.
            shortest_route = nx.dijkstra_path(
                self.graph,
                source=start,
                target=destination,
                weight="distance"
            )

            shortest_distance = self.get_route_distance(shortest_route)
            recommended_distance = self.get_route_distance(
                recommended_route
            )

            extra_distance = round(
                recommended_distance - shortest_distance, 2
            )

            return {
                "route": recommended_route,
                "total_cost": round(recommended_cost, 2),
                "distance": recommended_distance,
                "shortest_route": shortest_route,
                "shortest_distance": shortest_distance,
                "extra_distance": extra_distance
            }

        except nx.NetworkXNoPath:
            return {
                "route": [],
                "total_cost": None,
                "distance": None,
                "shortest_route": [],
                "shortest_distance": None,
                "extra_distance": None,
                "message": "No path exists between these locations."
            }