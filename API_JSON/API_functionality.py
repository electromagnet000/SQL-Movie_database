import json
import requests

def API_add_movie(title):

        # using my api key I can get access to the OMDB api
        API_KEY = "ae79a6f6"
        # sends a get request to gather specific information from Movies API
        api_url = "http://www.omdbapi.com/?t={}&apikey={}".format(title, API_KEY)
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        # if the response status is 200 then it proceeds with the request
        if response.status_code == requests.codes.ok:
            # creates a variable for the text repsonse

            fetched_data = response.json()

            # creates an empty dict with an id number for the film
            requested_data = {}

            # creates the parameters we need to get
            requested_parameters = ['Title', 'Year', 'imdbRating', 'Poster', 'imdbID']

            # iterates through the keys to get the correct parameters and stores them in requested_data
            for key, value in fetched_data.items():
                if key in requested_parameters:
                    requested_data[key] = value

            # checks if anything was actually fetched
            try:
                if not requested_data['Title']:
                    return f"Movie {title} not found in API"
            except KeyError as e:
                return f"Movie {title} not found in API database"

            return requested_data
