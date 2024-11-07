import weather_nominatim
import weather_path
import time
from json.decoder import JSONDecodeError
from urllib.error import URLError
from urllib.error import HTTPError
    
def run() -> None:
    '''
    Gets user inputs for the method of search they want to use, and uses a
    while loop to continuously collect desired queries until requested to stop.
    '''
    target = input()
    weather = input()
    list_of_queries = []
    while True:
        query = input()
        list_of_queries.append(query)
        if query == 'NO MORE QUERIES':
            break
    reverse = input()
    process_target(target, weather, list_of_queries, reverse)


def process_target(target: str, weather: str, list_of_queries: list[str], reverse: str) -> list[str]:
    '''
    Processes all of the users input. Contains list of desired outputs that prints
    at the end of the function.
    '''
    results = []
    try:
        '''Sets variable t to target object depending on user input, and gets
        latitude and longitude'''
        if target.startswith('TARGET FILE '):
            target_file = target[12:]
            t = weather_path.TargetFile(target_file)

        elif target.startswith('TARGET NOMINATIM '):
            target_nominatim = target[17:]
            t = weather_nominatim.TargetNominatim(target_nominatim)
        lat = t.get_latitude()
        lon = t.get_longitude()
        results.append(f'TARGET {get_lat(lat)} {get_lon(lon)}')
        '''Sets variable w to weather database object depending on user input,
        creating a polygon variable storing the average polygon coordinates'''
        if weather.startswith('WEATHER FILE '):
            weather_file = weather[13:]
            w = weather_path.WeatherFile(weather_file)
        elif weather == 'WEATHER NWS':
            w = weather_nominatim.WeatherNominatim(lat, lon)
        polygon = w.get_polygon()
        'Processes every query from the list of queries'
        for query in list_of_queries:
            if query.startswith('TEMPERATURE AIR '):
                x = query.split(' ')
                x[3] = int(x[3])
                results.append(w.temperature_air(x[2], x[3], x[4]))
            elif query.startswith('TEMPERATURE FEELS '):
                x = query.split(' ')
                x[3] = int(x[3])
                results.append(w.temperature_feels(x[2], x[3], x[4]))
            elif query.startswith('HUMIDITY '):
                x = query.split(' ')
                x[1] = int(x[1])
                results.append(w.humidity(x[1], x[2]))
            elif query.startswith('WIND '):
                x = query.split(' ')
                x[1] = int(x[1])
                results.append(w.wind(x[1], x[2]))
            elif query.startswith('PRECIPITATION'):
                x = query.split(' ')
                x[1] = int(x[1])
                results.append(w.precipitation(x[1], x[2]))
        '''Sets variable r to reverse object, and reverse searches for a description
        of the closest location to the desired location'''
        if reverse == 'REVERSE NOMINATIM':
            'Pauses program for 1 second given the nominatim restriction'
            if target.startswith('TARGET NOMINATIM '):
                time.sleep(1)
            r = weather_nominatim.ReverseNominatim(polygon[0],polygon[1])
        elif reverse.startswith('REVERSE FILE '):
            r_file = reverse[13:]
            r = weather_path.ReverseFile(r_file)
        results.insert(1, r.get_display_name())
        'Credits'
        if target.startswith('TARGET NOMINATIM '):
            results.append('**Forward geocoding data from OpenStreetMap')
        if reverse == 'REVERSE NOMINATIM':
            results.append('**Reverse geocoding data from OpenStreetMap')
        if weather == 'WEATHER NWS':
            results.append('**Real-time weather data from National Weather Service, United States Department of Commerce')
    except FileNotFoundError:
        "Can't find file"
        print('FAILED')
        print(target_file)
        print('MISSING')
    except JSONDecodeError as e:
        "File is not json"
        print('FAILED')
        print(target_file)
        print('FORMAT')
    except URLError:
        "Not connected to the internet"
        print('FAILED')
        print(target_nominatim)
        print('NETWORK')
    except HTTPError as err:
        "If HTTP status code is not 200"
        if err.code != 200:
            print('FAILED')
            print(f'{err.code} {target_nominatim}')
            print('NOT 200')
    for i in results:
        '''Prints results in the order they were stored in in the list of queries, along with location name and
        proper credits'''
        print(i)

def get_lat(latitude: float) -> str:
    'Returns a string with the latitude in the desired format listed in specifications.'
    if latitude > 0:
        return str(latitude) + '/N'
    elif latitude < 0:
        latitude = abs(latitude)
        return str(latitude) + '/S'
    else:
        return str(latitude) + '/E'

def get_lon(longitude: float) -> str:
    'Returns a string with the longitude in the desired format listed in specifications.'
    if longitude > 0:
        return str(longitude) + '/E'
    elif longitude < 0:
        longitude = abs(longitude)
        return str(longitude) + '/W'
    else:
        return str(longitude) + '/M'



if __name__ == '__main__':
    run()
