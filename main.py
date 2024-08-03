import data
from datetime import datetime
import pandas as pd
from plotting import (
    plot_delayed_flights_by_airline, plot_delayed_flights_by_hour,
    plot_heatmap_routes, plot_delayed_flights_map
)

SQLITE_URI = 'sqlite:///flights.sqlite3'
IATA_LENGTH = 3


def get_airports_data(data_manager):
    """
    Fetches airport data from the database and returns it as a pandas DataFrame.
    Handles empty values in LATITUDE and LONGITUDE.
    """
    airport_records = data_manager.get_airports()
    data = {
        'IATA_CODE': [record['IATA_CODE'] for record in airport_records],
        'latitude': [
            float(record['LATITUDE']) if record['LATITUDE'] else None
            for record in airport_records
        ],
        'longitude': [
            float(record['LONGITUDE']) if record['LONGITUDE'] else None
            for record in airport_records
        ]
    }
    # Filter out records with None values for latitude or longitude
    valid_data = {key: [] for key in data}
    for i in range(len(data['IATA_CODE'])):
        if data['latitude'][i] is not None and data['longitude'][i] is not None:
            for key in data:
                valid_data[key].append(data[key][i])
    return pd.DataFrame(valid_data).set_index('IATA_CODE')


def delayed_flights_by_airline(data_manager):
    """
    Asks the user for an airline name and prints delayed
    flights for that airline.
    """
    airline_input = input("Enter airline name: ")
    try:
        results = data_manager.get_delayed_flights_by_airline(airline_input)
        print_results(results)
    except AttributeError as e:
        print(f"Error: {e}. Please check if the function is implemented.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def delayed_flights_by_airport(data_manager):
    """
    Asks the user for a 3-letter IATA airport code and prints delayed
    flights for that airport.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    try:
        results = data_manager.get_delayed_flights_by_airport(airport_input)
        print_results(results)
    except AttributeError as e:
        print(f"Error: {e}. Please check if the function is implemented.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


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
            print(f"{result['FLIGHT_ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes")
        else:
            print(f"{result['FLIGHT_ID']}. {origin} -> {dest} by {airline}")


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
    5: (lambda data_manager: plot_delayed_flights_by_airline(data_manager.get_all_flights()),
        "Plot delayed flights by airline"),
    6: (lambda data_manager: plot_delayed_flights_by_hour(data_manager.get_all_flights()),
        "Plot delayed flights by hour"),
    7: (lambda data_manager: plot_heatmap_routes(data_manager.get_all_flights()),
        "Plot heatmap of delayed flights by route"),
    8: (lambda data_manager: plot_delayed_flights_map(data_manager.get_all_flights(), airports),
        "Plot map of delayed flights by route"),
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
