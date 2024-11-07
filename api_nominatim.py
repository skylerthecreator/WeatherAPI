import json
import urllib.parse
import urllib.request
import datetime

class TargetNominatim:
    '''
    Process user's input if they wish to search via description of a location.
    Finds the coordinates of the location retrieved and stores in itself.
    '''
    def __init__(self, target: str):
        request = urllib.request.Request(
            self._get_target_url(target),
            headers = {'Referer': 'https://www.ics.uci.edu/~thornton/ics32a/ProjectGuide/Project3/tianzhs'}
        )
        response = urllib.request.urlopen(request)
        decoded = response.read().decode(encoding = 'utf-8')
        features = json.loads(decoded)
        list_features = features['features']
        coordinates = list_features[0]['geometry']['coordinates']
        self._longitude = float(coordinates[0])
        self._latitude = float(coordinates[1])

    def _get_target_url(self, target: str) -> str:
        'Returns correctly parsed url given the search descriptions'
        search = urllib.parse.urlencode([('q',target),('format','geojson')])
        return f'https://nominatim.openstreetmap.org/search?{search}'

    def get_latitude(self) -> float:
        return self._latitude

    def get_longitude(self) -> float:
        return self._longitude

class WeatherNominatim:
    '''
    Process user's input if they choose to use API website to get their hourly
    forecast data. Finds the hourly forecast geojson url from the given
    coordinates. init function stores the library from the found geojson,
    as well as the library inside 'properties' -> 'periods' which gives the
    hourly forecast.
    '''
    def __init__(self, latitude: float, longitude: float):
        
        request = urllib.request.Request(
            self._get_weather_url(latitude, longitude),
            headers = {'User-Agent': '(https://www.ics.uci.edu/~thornton/ics32a/ProjectGuide/Project3, tianzhs@uci.edu)'}
        )
        response = urllib.request.urlopen(request)
        decoded = response.read().decode(encoding = 'utf-8')
        info = json.loads(decoded)
        forecast_hourly_url = info['properties']['forecastHourly']

        fh_request = urllib.request.Request(
            forecast_hourly_url,
            headers = {'User-Agent': '(https://www.ics.uci.edu/~thornton/ics32a/ProjectGuide/Project3, tianzhs@uci.edu)'}
        )
        fh_response = urllib.request.urlopen(fh_request)
        fh_decoded = fh_response.read().decode(encoding = 'utf-8')
        fh_info = json.loads(fh_decoded)
        self._info = fh_info
        self._forecast = fh_info['properties']['periods']

    '''
    NOTE: most functions below are nearly identical to the ones that exist in
    weather_path.py, hence the docstrings will also be the same. These are all
    used to process individual queries requested by the user.
    '''
    def temperature_air(self, scale: str, length: int, limit: str) -> str:
        '''
        Returns string with the time that the max/min temperature occurs,
        followed by that temperature in the desired scale, 
        '''
        temp = None
        time = None
        for i in range(length):
            fc = self._forecast[i]['temperature']
            if temp == None:
                temp = fc
                time = self._forecast[i]['startTime']
            elif limit == 'MAX' and fc > temp:
                temp = fc
                time = self._forecast[i]['startTime']
            elif limit == 'MIN' and fc < temp:
                temp = fc
                time = self._forecast[i]['startTime']
        if scale == 'C':
            temp = (temp - 32) * (5 / 9)
        time = self._proper_time(time)
        return time + ' ' + f'{temp:.4f}'
    
    def temperature_feels(self, scale: str, length: int, limit: str) -> str:
        '''
        Returns string with the time that the max/min "feels temperature"
        occurs, followed by that "feels temperature" in the desired scale.
        '''
        temp = None
        time = None
        humidity = None
        wind = None
        feels_like = None
        for i in range(length):
            temp = self._forecast[i]['temperature']
            time = self._forecast[i]['startTime']
            humidity = self._forecast[i]['relativeHumidity']['value']
            wind = self._forecast[i]['windSpeed']
            windspeed = float(wind[:wind.find(' ')])
            fl = self._get_feels_like(temp, humidity, windspeed)
            if feels_like == None:
                feels_like = fl
            elif limit == 'MAX' and fl > feels_like:
                time = self._forecast[i]['startTime']
                feels_like = fl
            elif limit == 'MIN' and fl < feels_like:
                time = self._forecast[i]['startTime']
                feels_like = fl
        if scale == 'C':
            feels_like = (feels_like - 32) * (5 / 9)
        time = self._proper_time(time)
        return time + ' ' + f'{feels_like:.4f}'

    def humidity(self, length: int, limit: str) -> str:
        '''
        Returns string with the time that the max/min humidity occurs, followed
        by that humidity value in farenheit.
        '''
        humidity = None
        time = None
        for i in range(length):
            h = self._forecast[i]['relativeHumidity']['value']
            if humidity == None:
                humidity = h
                time = self._forecast[i]['startTime']
            elif limit == 'MAX' and h > humidity:
                humidity = h
                time = self._forecast[i]['startTime']
            elif limit == 'MIN' and h < humidity:
                humidity = h
                time = self._forecast[i]['startTime']
        time = self._proper_time(time)
        return f'{time} {humidity:.4f}%'

    def wind(self, length: int, limit: str) -> str:
        '''
        Returns string with the time that the max/min windspeed occurs, followed
        by the speed in mph.
        '''
        wind = None
        time = None
        for i in range(length):
            w = self._forecast[i]['windSpeed']
            w = float(w[:w.find(' ')])
            if wind == None:
                wind = w
                time = self._forecast[i]['startTime']
            elif limit == 'MAX' and w > wind:
                wind = w
                time = self._forecast[i]['startTime']
            elif limit == 'MIN' and w < wind:
                wind = w
                time = self._forecast[i]['startTime']
        time = self._proper_time(time)
        return f'{time} {wind:.4f}'

    def precipitation(self, length: int, limit: str) -> str:
        '''
        Returns string with the time that the max/min precipitation occurs,
        followed by the precipitation value in farenheit.
        '''
        precipitation = None
        time = None
        for i in range(length):
            p = self._forecast[i]['probabilityOfPrecipitation']['value']
            if precipitation == None:
                precipitation = p
                time = self._forecast[i]['startTime']
            elif limit == 'MAX' and p > precipitation:
                precipitation = p
                time = self._forecast[i]['startTime']
            elif limit == 'MIN' and p < precipitation:
                precipitation = p
                time = self._forecast[i]['startTime']
        time = self._proper_time(time)
        return f'{time} {precipitation:.4f}%'

    def _proper_time(self, time: str) -> str:
        '''
        Converts a time string in the format given by the nominatim to the
        format given in the specifications, adjusted for UTC time zone.
        '''
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hours = int(time[11:13])
        minutes = int(time[14:16])
        seconds = int(time[17:19])
        dt = datetime.datetime(year, month, day, hours, minutes, seconds)
        nt = dt.astimezone(datetime.timezone.utc)
        nt = str(nt)
        new_string = nt[0:nt.find(' ')] + 'T' + nt[nt.find(' ') + 1:]
        new_string = new_string[:-6] + 'Z'
        return new_string

    
    def _get_weather_url(self, latitude: float, longitude: float) -> str:
        'Returns the API weather url value with the proper latitude and longitude.'
        return f'https://api.weather.gov/points/{latitude},{longitude}'
    
    def _get_feels_like(self, temp: float, humidity: float, windspeed: float) -> float:
        '''
        Calculates the feels like temperature using the formula listed in the
        project notes. Generic naming since it isn't specified what each number
        represents.
        '''
        if temp >= 68:
            a = -42.379
            b = 2.04901523 * temp
            c = 10.14333127 * humidity
            d = -0.22475541 * temp * humidity
            e = -0.00683783 * pow(temp, 2)
            f = -0.05481717 * pow(humidity, 2)
            g = 0.00122874 * pow(temp, 2) * humidity
            h = 0.00085282 * temp * pow(humidity, 2)
            i = -0.00000199 * pow(temp, 2) * pow(humidity, 2)
            return a + b + c + d + e + f + g + h + i
        elif temp <= 50 and windspeed > 3:
            a = 35.74
            b = 0.6215 * temp
            c = -35.75 * pow(windspeed, 0.16)
            d = 0.4275 * temp * pow(windspeed, 0.16)
            return a + b + c + d
        else:
            return temp
    
    def get_polygon(self) -> tuple:
        '''
        Gets the average latitude and longitude from all the coordinates listed
        in the polygon in the API website.
        '''
        polygon = self._info['geometry']['coordinates'][0]
        all_latitudes = []
        for coordinate in polygon:
            unique = True
            for i in all_latitudes:
                if coordinate[1] == i:
                    unique = False
            if unique:
                all_latitudes.append(coordinate[1])
        total_lat = 0
        for latitude in all_latitudes:
            total_lat += latitude
        avg_lat = total_lat / len(all_latitudes)
        all_longitudes = []
        for coordinate in polygon:
            unique = True
            for i in all_longitudes:
                if coordinate[0] == i:
                    unique = False
            if unique:
                all_longitudes.append(coordinate[0])
        total_lon = 0
        for longitude in all_longitudes:
            total_lon += longitude
        avg_lon = total_lon / len(all_longitudes)
        return (avg_lat, avg_lon)

class ReverseNominatim:
    '''
    Process user's input if they choose to use nominatim to reverse search for
    the nearest weather station given the polygon coordinates. Stores the
    description of the location that is stored in 'display_name' in a self
    variable.
    '''
    def __init__(self, latitude: float, longitude: float):
        request = urllib.request.Request(
            self._get_reverse_url(latitude, longitude),
            headers = {'Referer': 'https://www.ics.uci.edu/~thornton/ics32a/ProjectGuide/Project3/tianzhs'}
        )
        response = urllib.request.urlopen(request)
        decoded = response.read().decode(encoding = 'utf-8')
        info = json.loads(decoded)
        self._display_name = info['features'][0]['properties']['display_name']
        
    def get_display_name(self) -> str:
        ''''
        Returns the description of the location listed inside "display_name"
        inside the 'properties' library, stored in a self variable from
        the init method.
        '''
        return self._display_name

    def _get_reverse_url(self, latitude: float, longitude: float) -> str:
        ''''
        Returns proper url that allows a reverse search on nominatim given the
        coordinates of the desired location.
        '''
        search = urllib.parse.urlencode([('lat',latitude),('lon',longitude),('format','geojson')])
        return f'https://nominatim.openstreetmap.org/reverse?{search}'


