from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

QUERY_FLIGHT_BY_ID = """
    SELECT flights.*, 
    airlines.airline, 
    flights.ID as FLIGHT_ID, 
    flights.DEPARTURE_DELAY as DELAY 
FROM flights 
JOIN airlines ON flights.airline = airlines.id 
WHERE flights.ID = :id
"""
QUERY_FLIGHTS_BY_DATE = """
SELECT 
    flights.*, 
    airlines.airline, 
    flights.ID as FLIGHT_ID, 
    flights.DEPARTURE_DELAY as DELAY 
FROM flights 
JOIN airlines ON flights.airline = airlines.id 
WHERE flights.YEAR = :year AND flights.MONTH = :month 
AND flights.DAY = :day
"""

QUERY_DELAYED_FLIGHTS_BY_AIRLINE = """
SELECT 
    flights.*, 
    airlines.airline, 
    flights.ID as FLIGHT_ID, 
    flights.DEPARTURE_DELAY as DELAY 
FROM flights 
JOIN airlines ON flights.airline = airlines.id 
WHERE airlines.airline = :airline 
AND flights.DEPARTURE_DELAY > 0
"""
QUERY_DELAYED_FLIGHTS_BY_AIRPORT = """
SELECT 
    flights.*, 
    airlines.airline, 
    flights.ID as FLIGHT_ID, 
    flights.DEPARTURE_DELAY as DELAY 
FROM flights 
JOIN airlines ON flights.airline = airlines.id 
WHERE flights.ORIGIN_AIRPORT = :airport 
AND flights.DEPARTURE_DELAY > 0
"""

QUERY_ALL_FLIGHTS = """
SELECT 
    flights.*, 
    airlines.airline, 
    flights.ID as FLIGHT_ID, 
    flights.DEPARTURE_DELAY as DELAY 
FROM flights 
JOIN airlines ON flights.airline = airlines.id
"""

QUERY_AIRPORTS = """
SELECT 
    IATA_CODE, 
    LATITUDE, 
    LONGITUDE 
FROM airports
"""


class FlightData:
    """
    The FlightData class is a Data Access Layer (DAL) object that provides an
    interface to the flight data in the SQLITE database.
    """

    def __init__(self, db_uri):
        """
        Initialize a new engine using the given database URI
        """
        self._engine = create_engine(db_uri)

    def _execute_query(self, query, params=None):
        """
        Execute an SQL query with the params provided in a dictionary,
        and returns a list of records (dictionary-like objects).
        If an exception was raised, print the error, and return an empty list.
        """
        try:
            with self._engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                # Use the keys from the result to construct dictionaries
                keys = result.keys()
                return [dict(zip(keys, row)) for row in result]
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return []

    def get_flight_by_id(self, flight_id):
        """
        Searches for flight details using flight ID.
        If the flight was found, returns a list with a single record.
        """
        params = {'id': flight_id}
        return self._execute_query(QUERY_FLIGHT_BY_ID, params)

    def get_flights_by_date(self, day, month, year):
        """
        Searches for flights by date.
        If flights are found, returns a list of records.
        """
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(QUERY_FLIGHTS_BY_DATE, params)

    def get_delayed_flights_by_airline(self, airline_name):
        """
        Searches for delayed flights for a specific airline.
        If flights are found, returns a list of records.
        """
        params = {'airline': airline_name}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

    def get_delayed_flights_by_airport(self, airport_code):
        """
        Searches for delayed flights from a specific airport.
        If flights are found, returns a list of records.
        """
        params = {'airport': airport_code}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

    def get_all_flights(self):
        """
        Fetches all flight records.
        """
        return self._execute_query(QUERY_ALL_FLIGHTS)

    def get_airports(self):
        """
        Fetches all airports with their IATA code,
        latitude, and longitude.
        """
        return self._execute_query(QUERY_AIRPORTS)

    def __del__(self):
        """
        Closes the connection to the database when the
        object is about to be destroyed
        """
        self._engine.dispose()
