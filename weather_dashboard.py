import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Weather Dashboard with Search and Forecasts"

# AccuWeather API settings
API_KEY = "5fkKqjA9uHqyCydycrC1nYGxL5t6JYuu"  # Replace with your actual API key
AUTOCOMPLETE_URL = "http://dataservice.accuweather.com/locations/v1/cities/autocomplete"
CURRENT_CONDITIONS_URL = "http://dataservice.accuweather.com/currentconditions/v1/"
FORECAST_5DAY_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/"
FORECAST_12HOUR_URL = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/"

# App layout
app.layout = html.Div(
    children=[
        html.H1("Real-Time Weather API", style={"textAlign": "center"}),
        html.Div(
            [
                # Search input
                dcc.Input(
                    id="city-search",
                    type="text",
                    placeholder="Search for a city...",
                    debounce=True,
                    style={"width": "60%", "padding": "10px", "marginBottom": "10px"}
                ),
                # Search button
                html.Button(
                    "Search",
                    id="search-button",
                    n_clicks=0,
                    style={"padding": "10px", "marginLeft": "10px"}
                ),
                # Dropdown for city selection
                dcc.Dropdown(
                    id="city-dropdown",
                    placeholder="Select a city from the list",
                    style={"width": "60%", "marginTop": "20px", "marginBottom": "20px"}
                ),
                # Current weather data
                html.Div(id="weather-data", style={"marginTop": "20px"}),
                # 5-day forecast data
                html.Div(id="forecast-data", style={"marginTop": "40px"}),
                # 12-hour forecast data
                html.Div(id="hourly-forecast-data", style={"marginTop": "40px"}),
            ]
        ),
    ],
    style={"padding": "20px"}
)

# Callback to fetch city suggestions when the search button is clicked
@app.callback(
    Output("city-dropdown", "options"),
    Input("search-button", "n_clicks"),
    State("city-search", "value")
)
def update_city_dropdown(n_clicks, search_query):
    if not search_query:
        return []
    params = {"apikey": API_KEY, "q": search_query}
    response = requests.get(AUTOCOMPLETE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{"label": f"{item['LocalizedName']}, {item['AdministrativeArea']['LocalizedName']} ({item['Country']['ID']})",
                 "value": item['Key']} for item in data]
    return []

# Callback to fetch weather data, 5-day forecast, and 12-hour forecast
@app.callback(
    [Output("weather-data", "children"),
     Output("forecast-data", "children"),
     Output("hourly-forecast-data", "children")],
    Input("city-dropdown", "value"),
    State("city-dropdown", "options")
)
def update_all_forecasts(location_key, options):
    if not location_key or not options:
        return (html.Div("Select a city to view weather data", style={"color": "gray"}), html.Div(), html.Div())

    # Get the selected city details from dropdown options
    selected_city = next((option["label"] for option in options if option["value"] == location_key), "Unknown Location")

    # Fetch current weather data
    current_weather_response = requests.get(f"{CURRENT_CONDITIONS_URL}{location_key}", params={"apikey": API_KEY})
    if current_weather_response.status_code != 200:
        return (html.Div("Error fetching current weather data", style={"color": "red"}), html.Div(), html.Div())

    current_weather_data = current_weather_response.json()[0]
    current_weather_div = html.Div(
        [
            html.H3(f"City: {selected_city}"),
            html.H5(f"Location Code: {location_key}"),
            html.H5(f"Temperature: {current_weather_data['Temperature']['Imperial']['Value']}°F"),
            html.H5(f"Weather: {current_weather_data['WeatherText']}"),
            html.H5(f"Observation Time: {current_weather_data['LocalObservationDateTime']}"),
        ],
        style={"backgroundColor": "#f9f9f9", "padding": "20px", "borderRadius": "5px"}
    )

    # Fetch 5-day forecast data
    forecast_response = requests.get(f"{FORECAST_5DAY_URL}{location_key}", params={"apikey": API_KEY})
    if forecast_response.status_code != 200:
        return (current_weather_div, html.Div("Error fetching 5-day forecast data", style={"color": "red"}), html.Div())

    forecast_data = forecast_response.json()["DailyForecasts"]
    forecast_div = html.Div(
        [
            html.H3("5-Day Forecast"),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5(f"Date: {day['Date'].split('T')[0]}"),
                            html.P(f"Min: {day['Temperature']['Minimum']['Value']}°F"),
                            html.P(f"Max: {day['Temperature']['Maximum']['Value']}°F"),
                            html.P(f"Day: {day['Day']['IconPhrase']}"),
                            html.P(f"Night: {day['Night']['IconPhrase']}"),
                        ],
                        style={"backgroundColor": "#e9e9e9", "padding": "10px", "margin": "10px", "borderRadius": "5px"}
                    )
                    for day in forecast_data
                ],
                style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}
            ),
        ]
    )

    # Fetch 12-hour forecast data
    hourly_response = requests.get(f"{FORECAST_12HOUR_URL}{location_key}", params={"apikey": API_KEY})
    if hourly_response.status_code != 200:
        return (current_weather_div, forecast_div, html.Div("Error fetching 12-hour forecast data", style={"color": "red"}))

    hourly_data = hourly_response.json()
    hourly_div = html.Div(
        [
            html.H3("12-Hour Forecast"),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5(f"Time: {hour['DateTime'].split('T')[1].split('-')[0]}"),
                            html.P(f"Temperature: {hour['Temperature']['Value']}°F"),
                            html.P(f"Condition: {hour['IconPhrase']}"),
                        ],
                        style={"backgroundColor": "#f0f0f0", "padding": "10px", "margin": "10px", "borderRadius": "5px"}
                    )
                    for hour in hourly_data
                ],
                style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}
            ),
        ]
    )

    return current_weather_div, forecast_div, hourly_div


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
