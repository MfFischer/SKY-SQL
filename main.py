import data
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import folium

SQLITE_URI = 'sqlite:///flights.sqlite3'
IATA_LENGTH = 3


def get_airports_data(data_manager):
    """
    Fetches airport data from the database and returns
    it as a pandas DataFrame.
    Handles empty values in LATITUDE and LONGITUDE.
    """
    airport_records = data_manager.get_airports()
    data = {
        'IATA_CODE': [record['IATA_CODE'] for record in airport_records],
        'latitude': [float(record['LATITUDE']) if record['LATITUDE']
                     else None for record in airport_records],
        'longitude': [float(record['LONGITUDE']) if record['LONGITUDE']
                      else None for record in airport_records]
    }
    # Filter out records with None values for latitude or longitude
    valid_data = {key: [] for key in data}
    for i in range(len(data['IATA_CODE'])):
        if (data['latitude'][i] is not None and data['longitude'][i]
                is not None):
            for key in data:
                valid_data[key].append(data[key][i])
    return pd.DataFrame(valid_data).set_index('IATA_CODE')


def delayed_flights_by_airline(data_manager):
    """
    Asks the user for an airline name and prints delayed flights
     for that airline.
    """
    airline_input = input("Enter airline name: ")
    results = data_manager.get_delayed_flights_by_airline(airline_input)
    print_results(results)


def delayed_flights_by_airport(data_manager):
    """
    Asks the user for a 3-letter IATA airport code and
    prints delayed flights for that airport.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = data_manager.get_delayed_flights_by_airport(airport_input)
    print_results(results)


def flight_by_id(data_manager):
    """
    Asks the user for a flight ID and prints the flight details.
    """
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except Exception:
            print("Try again...")
        else:
            valid = True
    results = data_manager.get_flight_by_id(id_input)
    print_results(results)


def flights_by_date(data_manager):
    """
    Asks the user for a date and prints flights for that date.
    """
    global date
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, '%d/%m/%Y')
        except ValueError as e:
            print("Try again...", e)
        else:
            valid = True
    try:
        results = data_manager.get_flights_by_date(date.day, date.month, date.year)
        print_results(results)
    except AttributeError as e:
        print("Error: Method not implemented.", e)
    except Exception as e:
        print("An unexpected error occurred.", e)


def print_results(results):
    """
    Prints the results of flight queries.
    """
    print(f"Got {len(results)} results.")
    for result in results:
        try:
            delay = int(result['DELAY']) if result['DELAY'] else 0
            origin = result['ORIGIN_AIRPORT']
            dest = result['DESTINATION_AIRPORT']
            airline = result['AIRLINE']
        except (ValueError, KeyError) as e:
            print("Error showing results: ", e)
            return
        if delay and delay > 0:
            print(
                f"{result['FLIGHT_ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes"
            )
        else:
            print(f"{result['FLIGHT_ID']}. {origin} -> {dest} by {airline}")


def plot_delayed_flights_by_airline(data_manager):
    """
    Plots the percentage of delayed flights by airline.
    """
    results = data_manager.get_all_flights()
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


def plot_delayed_flights_by_hour(data_manager):
    """
    Plots the percentage of delayed flights by hour of
    the day using an enhanced bar plot.
    """
    results = data_manager.get_all_flights()
    hour_delays = {hour: {'total': 0, 'delayed': 0} for hour in range(24)}

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
        hour_delays[hour]['delayed'] / hour_delays[hour]['total'] *
        100 if hour_delays[hour]['total'] > 0 else 0 for
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
    cbar = plt.colorbar(sm, ticks=np.arange(0, 24, 1),
                        label='Hour of Day', ax=bar_plot.axes)

    plt.tight_layout()
    plt.show()


def plot_heatmap_routes(data_manager):
    """
    Plots a heatmap of the percentage of delayed
    flights by route (origin to destination).
    """
    results = data_manager.get_all_flights()
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
                               route_delays[route]['total'] * 100
                               for route in routes]
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


def plot_delayed_flights_map(data_manager):
    """
    Plots an interactive map of the percentage of delayed flights
    by route (origin to destination) focusing on the
    United States using Folium.
    """
    results = data_manager.get_all_flights()
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

    for route, counts in route_delays.items():
        origin, destination = route
        if origin in airports.index and destination in airports.index:
            origin_coords = [airports.loc[origin]['latitude'],
                             airports.loc[origin]['longitude']]
            destination_coords = [airports.loc[destination]['latitude'],
                                  airports.loc[destination]['longitude']]
            delay_percentage = counts['delayed'] / counts['total']
            color = plt.cm.Reds(delay_percentage)
            color_hex = (f'#{int(color[0] * 255):02x}'
                         f'{int(color[1] * 255):02x}{int(color[2] * 255):02x}')

            if delay_percentage < 0.2:
                group = delay_groups['Low Delay']
            elif delay_percentage < 0.4:
                group = delay_groups['Medium Delay']
            else:
                group = delay_groups['High Delay']

            folium.PolyLine(
                locations=[origin_coords, destination_coords],
                color=color_hex,
                weight=2,
                opacity=0.6
            ).add_to(group)

    for group in delay_groups.values():
        group.add_to(flight_map)

    folium.LayerControl().add_to(flight_map)

    # Save the map as an HTML file
    flight_map.save('delayed_flights_map.html')


def show_menu_and_get_input():
    """
    Shows the menu and gets user input for the function to execute.
    """
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    while True:
        try:
            choice = int(input())
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError:
            pass
        print("Try again...")


FUNCTIONS = {
    1: (flight_by_id, "Show flight by ID"),
    2: (flights_by_date, "Show flights by date"),
    3: (delayed_flights_by_airline, "Delayed flights by airline"),
    4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
    5: (plot_delayed_flights_by_airline, "Plot delayed flights by airline"),
    6: (plot_delayed_flights_by_hour, "Plot delayed flights by hour"),
    7: (plot_heatmap_routes, "Plot heatmap of delayed flights by route"),
    8: (plot_delayed_flights_map, "Plot map of delayed flights by route"),
    9: (quit, "Exit")
}


def main():
    """
    Main function to run the application.
    """
    data_manager = data.FlightData(SQLITE_URI)
    global airports
    airports = get_airports_data(data_manager)
    while True:
        choice_func = show_menu_and_get_input()
        try:
            choice_func(data_manager)
        except AttributeError as e:
            print(f"Error: {e}. Please check if the function is implemented.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
