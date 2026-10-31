import streamlit as st
from classes.style_manager import StyleManager
from classes.ar_manger import ARManager
from classes.corridor_crowd import CrowdManager
from classes.Route_Manager import RouteManager


st.markdown(
    """
    <h2 class="camera-title">EXORA | AR Navigation</h2>
    <p class="camera-description">
        Explore the exhibition using your camera.
    </p>
    """,
    unsafe_allow_html=True
)


# Initialize Managers

crowd_manager = CrowdManager()
route_manager = RouteManager(crowd_manager)


# Build Graph

if route_manager.graph.number_of_nodes() == 0:
    route_manager.build_graph()

if route_manager.graph.number_of_nodes() == 0:
    st.error("No locations found in the graph.")
    st.stop()


# Get Available Locations

location_ids = list(route_manager.graph.nodes)


# Select Starting Point

current_location = st.query_params.get("at", "TP_ENT")

if current_location not in location_ids:
    current_location = location_ids[0]


col1, col2 = st.columns(2)

with col1:
    start = st.selectbox(
        "You are at",
        location_ids,
        index=location_ids.index(current_location),
        format_func=lambda location_id: (
            route_manager.graph.nodes[location_id]["name"]
        )
    )

with col2:
    destination_ids = [
        location_id
        for location_id in location_ids
        if location_id != start
    ]

    goal = st.selectbox(
        "Destination",
        destination_ids,
        index=(
            destination_ids.index("SA_EXT")
            if "SA_EXT" in destination_ids
            else 0
        ),
        format_func=lambda location_id: (
            route_manager.graph.nodes[location_id]["name"]
        )
    )


st.divider()


# Find Recommended Route

if st.button("Find Best Route", use_container_width=True):

    result = route_manager.find_route(start, goal)

    if not result.get("route"):

        st.error(
            result.get("message", "No route found.")
        )

    else:

        path = result["route"]

        st.session_state["ar_route"] = path
        st.session_state["ar_destination"] = goal
        st.session_state["ar_start"] = start


# Display Route

if "ar_route" in st.session_state:

    path = st.session_state["ar_route"]

    if (
        st.session_state["ar_start"] != start
        or st.session_state["ar_destination"] != goal
    ):
        st.session_state.pop("ar_route", None)
        st.rerun()

    else:

        st.success("Route found!")

        route_names = [
            route_manager.graph.nodes[location_id]["name"]
            for location_id in path
        ]

        st.markdown("### Recommended Route")

        st.write(" → ".join(route_names))

        # Calculate Route Distance

        route_distance = 0

        for i in range(len(path) - 1):

            edge_data = route_manager.graph[
                path[i]
            ][
                path[i + 1]
            ]

            distance = edge_data.get(
                "distance",
                edge_data.get("distance_m", 0)
            )

            route_distance += float(distance)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Route Distance",
                f"{route_distance:.1f} meters"
            )

        with col2:
            st.metric(
                "Total Route Cost",
                f"{result['total_cost']:.1f}"
                if "result" in locals()
                else "Calculated"
            )

        st.divider()

        # AR Navigation

        if len(path) > 1:

            current_id = path[0]
            next_id = path[1]

            next_data = route_manager.graph.nodes[next_id]
            destination_data = route_manager.graph.nodes[goal]

            edge_data = route_manager.graph[
                current_id
            ][
                next_id
            ]

            next_distance = edge_data.get(
                "distance",
                edge_data.get("distance_m", 0)
            )

            st.markdown("###  AR Navigation")

            ARManager().camera_view(
                target_bearing=0,
                next_name=next_data["name"],
                next_distance=next_distance,
                destination=destination_data["name"]
            )

        else:

            st.success(
                "You have arrived at your destination! "
            )