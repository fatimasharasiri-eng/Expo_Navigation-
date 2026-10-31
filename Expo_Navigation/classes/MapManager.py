import plotly.graph_objects as go
import streamlit as st


class MapManager:
    def __init__(self, crowd_manager, route_manager):
        self.crowd_manager = crowd_manager
        self.route_manager = route_manager

        self.colors = {
            "low": "#CDE8D5",
            "medium": "#F5D98E",
            "high": "#F2B8B5",
            "route": "#2478E5",
            "wall": "#D7DCD6",
            "room": "#FFFFFF",
            "text": "#26352D",
        }

        self.positions = {
            "TP_ENT": (1, 5),
            "MC1": (3, 5),
            "MC2": (6, 5),
            "MC3": (9, 5),
            "MC4": (12, 5),
            "TP_EXT": (14, 5),

            "SA_ENT": (3, 7),
            "SA_C1": (3, 8.5),
            "SA_C2": (5, 8.5),
            "SA_C3": (6, 9.5),
            "SA_C4": (3, 10),
            "SA_EXT": (3, 11.5),

            "JP_ENT": (6, 3),
            "JP_C1": (6, 1.8),
            "JP_C2": (7.5, 1.8),
            "JP_C3": (8.5, 1),
            "JP_C4": (6, 0.3),
            "JP_EXT": (6, -1),

            "FR_ENT": (9, 3),
            "FR_C1": (9, 1.8),
            "FR_C2": (10.5, 1.8),
            "FR_C3": (11, 1),
            "FR_C4": (9, 0.3),
            "FR_EXT": (9, -1),

            "WC1": (6, 7),
            "WS1": (9, 7),
            "ID1": (1, 7),
            "FA1": (12, 7),
        }

    def _crowd_color(self, source, destination):
        # Use the same crowd thresholds as CrowdManager.
        level = self.crowd_manager.get_crowd_level(
            source, destination
        )

        colors = {
            "Low": self.colors["low"],
            "Medium": self.colors["medium"],
            "High": self.colors["high"],
            "Unknown": self.colors["wall"],
        }

        return colors.get(level, self.colors["wall"])

    def _add_room(
        self,
        fig,
        x,
        y,
        label,
        width=1.45,
        height=0.65,
        fill=None,
        font_size=10,
        line_color=None,
    ):
        fig.add_shape(
            type="rect",
            x0=x - width / 2,
            x1=x + width / 2,
            y0=y - height / 2,
            y1=y + height / 2,
            fillcolor=fill or self.colors["room"],
            line=dict(
                color=line_color or self.colors["wall"],
                width=1,
            ),
            layer="above",
        )

        fig.add_annotation(
            x=x,
            y=y,
            text=label,
            showarrow=False,
            font=dict(
                size=font_size,
                color=self.colors["text"],
            ),
            align="center",
        )

    def _add_zone(self, fig, x0, y0, x1, y1, title, fill):
        fig.add_shape(
            type="rect",
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            fillcolor=fill,
            opacity=0.7,
            line=dict(color="#DDE4DC", width=1),
            layer="below",
        )

        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=y1 - 0.35,
            text=f"<b>{title}</b>",
            showarrow=False,
            font=dict(size=13, color="#365644"),
        )

    def _add_corridor_edge(
        self,
        fig,
        source,
        destination,
        color,
        width,
        is_route=False,
    ):
        x1, y1 = self.positions[source]
        x2, y2 = self.positions[destination]

        # Draw right-angle corridor paths.
        if abs(x1 - x2) > 0.01 and abs(y1 - y2) > 0.01:
            middle_x = (x1 + x2) / 2
            xs = [x1, middle_x, middle_x, x2]
            ys = [y1, y1, y2, y2]
        else:
            xs = [x1, x2]
            ys = [y1, y2]

        rate = self.crowd_manager.get_crowd_rate(
            source, destination
        ) * 100

        level = self.crowd_manager.get_crowd_level(
            source, destination
        )

        route_label = (
            "Recommended route"
            if is_route
            else "Regular corridor"
        )

        hover_text = (
            f"<b>{source} ↔ {destination}</b>"
            f"<br>Crowd level: {level}"
            f"<br>Occupancy: {rate:.1f}%"
            f"<br>{route_label}"
        )

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line=dict(
                    color=color,
                    width=width,
                    shape="linear",
                ),
                text=[hover_text] * len(xs),
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            )
        )

    def render(
        self,
        route_result=None,
        start=None,
        destination=None,
    ):
        fig = go.Figure()

        # Pavilion zones.
        self._add_zone(
            fig, 1.8, 7.7, 6.8, 10.7,
            "SAUDI ARABIA PAVILION", "#F1F6EF"
        )

        self._add_zone(
            fig, 4.8, -0.5, 8.2, 2.5,
            "JAPAN PAVILION", "#F5F3EB"
        )

        self._add_zone(
            fig, 7.8, -0.5, 11.8, 2.5,
            "FRANCE PAVILION", "#F3F1F7"
        )

        # Main corridor background.
        fig.add_shape(
            type="rect",
            x0=0.5,
            x1=14.5,
            y0=4.45,
            y1=5.55,
            fillcolor="#E8ECE7",
            line=dict(color="#D5DCD4", width=1),
            layer="below",
        )

        fig.add_annotation(
            x=7.5,
            y=5.85,
            text="<b>MAIN CORRIDOR</b>",
            showarrow=False,
            font=dict(size=12, color="#52665A"),
        )

        graph = self.route_manager.graph

        route = []
        if route_result and route_result.get("route"):
            route = route_result["route"]

        route_edges = {
            frozenset((route[i], route[i + 1]))
            for i in range(len(route) - 1)
        }

        # Draw regular corridors first.
        # Draw the recommended route on top.
        edges = list(graph.edges())

        edges.sort(
            key=lambda edge: (
                frozenset(edge) in route_edges
            )
        )

        for source, target in edges:
            if (
                source not in self.positions
                or target not in self.positions
            ):
                continue

            is_route = (
                frozenset((source, target)) in route_edges
            )

            color = (
                self.colors["route"]
                if is_route
                else self._crowd_color(source, target)
            )

            width = 4.5 if is_route else 2.5

            self._add_corridor_edge(
                fig,
                source,
                target,
                color,
                width,
                is_route=is_route,
            )

        # Main corridor rooms.
        for node in ["MC1", "MC2", "MC3", "MC4"]:
            x, y = self.positions[node]

            self._add_room(
                fig, x, y, node,
                width=1.05,
                height=0.62,
            )

        # Entrances and exits.
        endpoint_labels = {
            "TP_ENT": "MAIN ENTRANCE",
            "TP_EXT": "MAIN EXIT",
            "SA_ENT": "ENTRANCE",
            "SA_EXT": "EXIT",
            "JP_ENT": "ENTRANCE",
            "JP_EXT": "EXIT",
            "FR_ENT": "ENTRANCE",
            "FR_EXT": "EXIT",
        }

        for node, label in endpoint_labels.items():
            x, y = self.positions[node]

            self._add_room(
                fig, x, y, label,
                width=1.45,
                height=0.62,
                fill="#EAF1E9",
                font_size=9,
            )

        # Pavilion sections.
        corridor_labels = {
            "SA_C1": "SAUDI 01",
            "SA_C2": "SAUDI 02",
            "SA_C3": "SAUDI 03",
            "SA_C4": "SAUDI 04",
            "JP_C1": "JAPAN 01",
            "JP_C2": "JAPAN 02",
            "JP_C3": "JAPAN 03",
            "JP_C4": "JAPAN 04",
            "FR_C1": "FRANCE 01",
            "FR_C2": "FRANCE 02",
            "FR_C3": "FRANCE 03",
            "FR_C4": "FRANCE 04",
        }

        for node, label in corridor_labels.items():
            x, y = self.positions[node]

            self._add_room(
                fig, x, y, label,
                width=1.4,
                height=0.58,
                font_size=9,
            )

        # Service locations.
        service_labels = {
            "ID1": "Information Desk",
            "WC1": "Restroom",
            "WS1": "Water Station",
            "FA1": "First Aid",
        }

        for node, label in service_labels.items():
            x, y = self.positions[node]

            self._add_room(
                fig, x, y, label,
                width=1.65,
                height=0.65,
                fill="#FFF9E9",
                font_size=8,
            )

        # Start and destination markers.
        markers = [
            (start, "START", "#198754"),
            (destination, "DESTINATION", "#2478E5"),
        ]

        for node, label, border in markers:
            if node not in self.positions:
                continue

            x, y = self.positions[node]

            fig.add_shape(
                type="rect",
                x0=x - 0.82,
                x1=x + 0.82,
                y0=y - 0.42,
                y1=y + 0.42,
                fillcolor="rgba(0,0,0,0)",
                line=dict(color=border, width=2),
                layer="above",
            )

            fig.add_annotation(
                x=x,
                y=y + 0.58,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=9, color=border),
            )

        # Legend.
        legend_items = [
            ("Low crowd", self.colors["low"]),
            ("Medium crowd", self.colors["medium"]),
            ("High crowd", self.colors["high"]),
            ("Recommended route", self.colors["route"]),
        ]

        for index, (label, color) in enumerate(legend_items):
            x = 0.8 + index * 3.45

            fig.add_shape(
                type="rect",
                x0=x,
                x1=x + 0.35,
                y0=12.15,
                y1=12.42,
                fillcolor=color,
                line=dict(color=color, width=1),
            )

            fig.add_annotation(
                x=x + 0.45,
                y=12.285,
                text=label,
                showarrow=False,
                xanchor="left",
                font=dict(size=10, color="#34473B"),
            )

        # Route summary.
        if route_result and route:
            distance = route_result.get("distance")

            if distance is not None:
                summary = (
                    f"<b>Recommended route distance:</b> "
                    f"{distance:.0f} m"
                )

                fig.add_annotation(
                    x=7.5,
                    y=13,
                    text=summary,
                    showarrow=False,
                    font=dict(size=12, color="#26352D"),
                )

        fig.update_layout(
            height=760,
            margin=dict(l=15, r=15, t=35, b=15),
            paper_bgcolor="#F8F8F4",
            plot_bgcolor="#F8F8F4",
            showlegend=False,
            hovermode="closest",
            xaxis=dict(
                visible=False,
                range=[0, 15],
                fixedrange=True,
            ),
            yaxis=dict(
                visible=False,
                range=[-1.8, 13.5],
                fixedrange=True,
                scaleanchor="x",
                scaleratio=1,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
            },
        )

    # Compatibility aliases.
    def show_map(
        self,
        route_result=None,
        start=None,
        destination=None,
    ):
        self.render(route_result, start, destination)

    def display_map(
        self,
        route_result=None,
        start=None,
        destination=None,
    ):
        self.render(route_result, start, destination)