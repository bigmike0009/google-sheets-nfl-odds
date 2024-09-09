import requests
import json
import os

CITYMAP = {
    'Falcons': 'Atlanta',
    'Ravens': 'Baltimore',
    'Bills': 'Buffalo',
    'Panthers': 'Carolina',
    'Bears': 'Chicago',
    'Bengals': 'Cincinnati',
    'Browns': 'Cleveland',
    'Cowboys': 'Dallas',
    'Broncos': 'Denver',
    'Lions': 'Detroit',
    'Packers': 'Green Bay',
    'Texans': 'Houston',
    'Colts': 'Indianapolis',
    'Jaguars': 'Jacksonville',
    'Chiefs': 'Kansas City',
    'Raiders': 'Las Vegas',
    'Chargers': 'Los Angeles',
    'Rams': 'Los Angeles',
    'Dolphins': 'Miami',
    'Vikings': 'Minnesota',
    'Patriots': 'New England',
    'Saints': 'New Orleans',
    'Giants': 'New York',
    'Jets': 'New York',
    'Eagles': 'Philadelphia',
    'Steelers': 'Pittsburgh',
    '49ers': 'San Francisco',
    'Seahawks': 'Seattle',
    'Buccaneers': 'Tampa Bay',
    'Titans': 'Tennessee',
    'Commanders': 'Washington',
    'Cardinals': 'Arizona'
}


def get_weather(team, time):

    api_key = os.environ['WEATHER_API_SECRET']
    city = CITYMAP[team]
    day = time.strftime('%Y-%m-%d')
    hour = time.strftime('%H')

    request_url = f"https://api.weatherapi.com/v1/forecast.json?q={city}&days=1&dt={day}&hour={hour}&key={api_key}"
    res = requests.get(request_url)

    data = res.json()
    hourly = data['forecast']['forecastday'][0]['hour'][0]

    returnStr = f'{hourly["temp_f"]}°F, {hourly["condition"]["text"]}'

    if hourly['chance_of_snow'] > 25:
        returnStr += f" ({hourly['chance_of_snow']}% chance of snow)"
    elif hourly['chance_of_rain'] > 25:
        returnStr += f" ({hourly['chance_of_rain']}% chance of rain)"
    elif hourly['wind_mph'] > 10:
        returnStr += f"({hourly['wind_mph']}+ MPH winds)"

    return returnStr