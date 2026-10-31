
import streamlit as st
from classes.corridor_crowd import CrowdManager
from classes.Route_Manager import RouteManager
from classes.MapManager import MapManager
from classes.style_manager import StyleManager

# Initialize managers.
crowd_manager = CrowdManager()
route_manager = RouteManager(crowd_manager)

# Build the graph before finding a route.
route_manager.build_graph()

map_manager = MapManager(
    crowd_manager,
    route_manager
)


st.title("Expo Navigation Map")

# Select the crowd scenario.
scenario = st.selectbox(
    "Crowd Scenario",
    list(crowd_manager.SCENARIOS.keys())
)

# Update crowd data.
crowd_manager.set_crowd_scenario(scenario)

# Get valid locations from the graph.
locations = list(route_manager.graph.nodes)

start = st.selectbox(
    "Starting Point",
    locations
)

destination = st.selectbox(
    "Destination",
    [node for node in locations if node != start]
)


if st.button("Find Best Route"):

    # Calculate the best route.
    route_result = route_manager.find_route(
        start,
        destination
    )

    # Check if a route exists.
    if route_result.get("route"):
        # Calculate crowd level for the recommended route.
        route = route_result["route"]

        crowd_rates = []

        for i in range(len(route) - 1):

            crowd_rate = crowd_manager.get_crowd_rate(
                route[i],
                route[i + 1]
            )

            crowd_rates.append(crowd_rate)

        # Calculate average crowd occupancy.
        if crowd_rates:

            average_crowd = (
                sum(crowd_rates) / len(crowd_rates)
            ) * 100

            if average_crowd < 40:
                crowd_level = "Low"
                crowd_icon = "🟢"

            elif average_crowd < 75:
                crowd_level = "Medium"
                crowd_icon = "🟡"

            else:
                crowd_level = "High"
                crowd_icon = "🔴"

            st.metric(
                label="Route Crowd Level",
                value=f"{crowd_icon} {crowd_level}",
                delta=f"{average_crowd:.1f}% occupancy"
            )
        # Display the map.
        map_manager.render(
            route_result=route_result,
            start=start,
            destination=destination,
        )

        # Display recommended route.
        st.success(
            "Recommended Route: "
            + " → ".join(route_result["route"])
        )

        # Display route cost.
        st.write(
            f"Route cost: {route_result['total_cost']}"
        )

        # Display distance only if available.
        if "distance" in route_result:
            st.write(
                f"Route distance: "
                f"{route_result['distance']} meters"
            )

    else:
        st.warning(
            route_result.get(
                "message",
                "No route is available."
            )
        )

