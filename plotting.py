import matplotlib.pyplot as plt
import seaborn as sns
import folium
import pandas as pd
import numpy as np


def plot_delayed_flights_by_airline(results):
    """
    Plots the percentage of delayed flights by airline.
    """
    airline_delays = {}

    for result in results:
        airline = result['AIRLINE']
        delay = int(result['DELAY']) if result['DELAY'] else 0
        if airline not in airline_delays:
            airline_delays[airline] = {'total': 0, 'delayed': 0}
        airline_delays[airline]['total'] += 1
        if delay > 0:
            airline_delays[airline]['delayed'] += 1

    airlines = list(airline_delays.keys())
    percentages = [airline_delays[airline]['delayed'] /
                   airline_delays[airline]['total'] * 100 for airline in airlines]

    plt.figure(figsize=(12, 8))
    sns.barplot(x=airlines, y=percentages)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Airline')
    plt.ylabel('Percentage of Delayed Flights')
    plt.title('Percentage of Delayed Flights by Airline')
    plt.tight_layout()
    plt.show()


def plot_delayed_flights_by_hour(results):
    """
    Plots the percentage of delayed flights by hour of the
    day using an enhanced bar plot.
    """
    hour_delays = {hour: {'total': 0, 'delayed': 0}
                   for hour in range(24)}

    for result in results:
        departure_time = result['DEPARTURE_TIME']
        delay = int(result['DELAY']) if result['DELAY'] else 0

        # Handle empty or malformed departure times
        try:
            hour = int(departure_time[:2])
            if hour < 0 or hour > 23:
                continue  # Skip invalid hour values
        except (ValueError, TypeError):
            continue

        hour_delays[hour]['total'] += 1
        if delay > 0:
            hour_delays[hour]['delayed'] += 1

    hours = np.arange(24)
    percentages = [
        hour_delays[hour]['delayed'] / hour_delays[hour]['total']
        * 100 if hour_delays[hour]['total'] > 0 else 0 for
        hour in hours]

    # Create an enhanced bar plot
    plt.figure(figsize=(12, 8))
    palette = sns.color_palette("coolwarm", as_cmap=True)
    colors = palette(np.linspace(0, 1, len(hours))).tolist()

    bar_plot = sns.barplot(x=hours, y=percentages, hue=hours,
                           palette=colors, dodge=False, legend=False)
    plt.xlabel('Hour of Day')
    plt.ylabel('Percentage of Delayed Flights')
    plt.title('Percentage of Delayed Flights by Hour of Day')

    # Create a color bar
    norm = plt.Normalize(0, 23)
    sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ticks=np.arange(0, 24, 1),
                 label='Hour of Day', ax=bar_plot.axes)

    plt.tight_layout()
    plt.show()


def plot_heatmap_routes(results):
    """
    Plots a heatmap of the percentage of delayed flights
    by route (origin to destination).
    """
    route_delays = {}

    for result in results:
        origin = result['ORIGIN_AIRPORT']
        destination = result['DESTINATION_AIRPORT']
        delay = int(result['DELAY']) if result['DELAY'] else 0
        route = (origin, destination)
        if route not in route_delays:
            route_delays[route] = {'total': 0, 'delayed': 0}
        route_delays[route]['total'] += 1
        if delay > 0:
            route_delays[route]['delayed'] += 1

    routes = list(route_delays.keys())
    data = {
        'Origin': [route[0] for route in routes],
        'Destination': [route[1] for route in routes],
        'Percentage Delayed': [route_delays[route]['delayed'] /
                               route_delays[route]['total']
                               * 100 for route in routes]
    }

    # Create a pivot table to format data for heatmap
    df = pd.DataFrame(data)
    pivot_table = df.pivot_table(values='Percentage Delayed',
                                 index='Origin', columns='Destination')

    plt.figure(figsize=(16, 12))
    sns.heatmap(pivot_table, cmap='Reds', annot=False)
    plt.xlabel('Destination Airport')
    plt.ylabel('Origin Airport')
    plt.title('Percentage of Delayed Flights by Route')
    plt.tight_layout()
    plt.show()


def plot_delayed_flights_map(results, airports):
    """
    Plots an interactive map of the percentage of delayed flights by route (origin to destination)
    focusing on the United States using Folium.
    """
    route_delays = {}

    for result in results:
        origin = result['ORIGIN_AIRPORT']
        destination = result['DESTINATION_AIRPORT']
        delay = int(result['DELAY']) if result['DELAY'] else 0
        route = (origin, destination)
        if route not in route_delays:
            route_delays[route] = {'total': 0, 'delayed': 0}
        route_delays[route]['total'] += 1
        if delay > 0:
            route_delays[route]['delayed'] += 1

    map_center = [37.0902, -95.7129]  # Center of the United States
    flight_map = folium.Map(location=map_center, zoom_start=4)

    delay_groups = {
        'Low Delay': folium.FeatureGroup(name='Low Delay (<20%)'),
        'Medium Delay': folium.FeatureGroup(name='Medium Delay (20-40%)'),
        'High Delay': folium.FeatureGroup(name='High Delay (>40%)')
    }

    def get_delay_color(delay_percentage):
        """
        Maps delay percentage to a color.
        - Green for low delay
        - Yellow for medium delay
        - Red for high delay
        """
        if delay_percentage < 0.2:
            return 'green'
        elif delay_percentage < 0.4:
            return 'yellow'
        else:
            return 'red'

    for route, counts in route_delays.items():
        origin, destination = route
        if origin in airports.index and destination in airports.index:
            origin_coords = [airports.loc[origin]['latitude'],
                             airports.loc[origin]['longitude']]
            destination_coords = [airports.loc[destination]['latitude'],
                                  airports.loc[destination]['longitude']]
            delay_percentage = counts['delayed'] / counts['total']
            color = get_delay_color(delay_percentage)

            if delay_percentage < 0.2:
                group = delay_groups['Low Delay']
            elif delay_percentage < 0.4:
                group = delay_groups['Medium Delay']
            else:
                group = delay_groups['High Delay']

            folium.PolyLine(
                locations=[origin_coords, destination_coords],
                color=color,
                weight=2,
                opacity=0.6
            ).add_to(group)

    for group in delay_groups.values():
        group.add_to(flight_map)

    folium.LayerControl().add_to(flight_map)

    # Save the map as an HTML file
    flight_map.save('delayed_flights_map.html')

