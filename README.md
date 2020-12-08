# FSND "Casting Agency" Capstone Project

## About

This is my capstone project for the Udacity Full Stack Web Developer nanodegree. It provides an API for a fictional casting agency. The API provides interaction with two object types (actors and movies) and manages authorization via three roles (casting assistant, casting director, and executive procucer). In addition, a mini-frontend is provided at the base URL to facilitate the creation of access tokens (JWT) via Auth0 implicit grant flow.

A live version of the app is hosted on Heroku: https://fsnd-capstone-vb.herokuapp.com/

## Contributors

- Viktor Brech
- FSND team (via provided starter code)

## Getting Started

### Installing Dependencies

#### Python 3.7

The app was written and tested in Python 3.7.9. We recommend working within a virtual environment ([python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/))

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

## Database Setup

The app will require a valid Postgres connection strinng in the `DATABASE_URL` environment variable. Heroku will set it automatically via the Postgres Add-On. When running the app locally, you should set this environment variable explicitly before running the flask server: 

```bash
export DATABASE_URL=postgres://...
```

## Running the server

There is a hosted version of the app running on https://fsnd-capstone-vb.herokuapp.com/ .

To run the server locally, however, execute:

```bash
source setup.sh
flask run
```

## API Reference

### Getting Started
- Base URL: This app is hosted on the base URL https://fsnd-capstone-vb.herokuapp.com/
- You can run the flask app locally, which will be on the base URL `http://127.0.0.1:5000/` by default
- Authentication: All API calls are authenticated via Bearer JWT, which is provisioned via Auth0. Access the authorization frontend via the base URL, and log in via Auth0 to generate a JWT. You can then use the token to authenticate calls to  hosted or localhost versions of the API

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```

The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable

In addition, the following authorization-related errors exist:
- 401: Invalid Header
- 401: Unauthorized
- 401: Invalid Claims
- 401: Token Expired
- 401: Authorization Header Missing


### Endpoint Library
```
GET "/actors"
GET "/movies"
DELETE "/actors/id"
DELETE "/movies/id"
POST "/actors"
POST "/movies"
PATCH "/actors/id"
PATCH "/movies/id"
```

#### GET "/actors"
- This endpoint fetches an array of all actors
- Request arguments: none.
- Returns: an array of key-value dictionaries containing each full actor object 
```
curl --location --request GET 'BASE_URL/actors' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN'
```
```
{
    "actors": [
        {
            "age": 30,
            "gender": "male",
            "id": 2,
            "name": "Jack Johnson"
        },
        {
            "age": 21,
            "gender": "male",
            "id": 4,
            "name": "Don Draper"
        }
    ],
    "success": true
}
```

#### GET "/movies"
- This endpoint fetches an array of all movies
- Request arguments: none.
- Returns: an array of key-value dictionaries representing each movie object
```
curl --location --request GET 'BASE_URL/movies' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN'
```
```
{
    "movies": [
        {
            "id": 2,
            "release_date": "2023-02-22",
            "title": "Armageddon 2"
        },
        {
            "id": 4,
            "release_date": "2046-01-27",
            "title": "Chungking Express 2"
        }
    ],
    "success": true
}
```

#### DELETE "/actors/{actor_id}"
- Deletes the actor with ID "actor_id" from the database
- Request arguments: none.
- Returns: a key "success" that equals true along with a key "delete" equal to the ID of the deleted actor 
```
curl --location --request DELETE 'BASE_URL/actors/3' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN'
```
```
{
    "delete": 3,
    "success": true
}
```

#### DELETE "/movies/{movie_id}"
- Deletes the movie with ID "movie_id" from the database
- Request arguments: none.
- Returns: a key "success" that equals true along with a key "delete" equal to the ID of the deleted movie 
```
curl --location --request DELETE 'BASE_URL/movies/2' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN'
```
```
{
    "delete": 2,
    "success": true
}
```

#### POST "/actors"
- Creates a new actor
- Request arguments: "name" string (required), "age" (integer, optional) and "gender" (enumeration options "male"/"female"/"other", optional)
- Returns: a key "success" that equals true along with a key "actor" that contains the just-created actor object as a dictionary inside an array
```
curl --location --request POST 'BASE_URL/actors' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Don Draper",
    "age": "18",
    "gender": "other"
}'
```
```
{
    "actors": [
        {
            "age": 18,
            "gender": "other",
            "id": 3,
            "name": "Don Draper"
        }
    ],
    "success": true
}
```

#### POST "/movies"
- Creates a new movie
- Request arguments: "title" string (required), "release_date", formatted as YYYY-MM-DD (optional)
- Returns: a key "success" that equals true along with a key "actor" that contains the just-created movie object as a dictionary inside an array
```
curl --location --request POST 'BASE_URL/movies' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data-raw '{
    "title": "Armageddon 2",
    "release_date": "2022-02-22"
}'
```
```
{
    "movies": [
        {
            "id": 2,
            "release_date": "2022-02-22",
            "title": "Armageddon 2"
        }
    ],
    "success": true
}
```

#### PATCH "/actors/{actor_id}"
- Updates the actor with the ID "actor_id"
- Request arguments: "name" string (optional), "age" (integer, optional) and "gender" (enumeration options "male"/"female"/"other", optional)
- Returns: a key "success" that equals true along with a key "actor" that contains the just-updated actor object as a dictionary inside an array
```
curl --location --request PATCH 'BASE_URL/actors/3' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data-raw '{
    "age": "21",
    "gender": "male"
}'
```
```
{
    "actors": [
        {
            "age": 21,
            "gender": "male",
            "id": 3,
            "name": "Don Draper"
        }
    ],
    "success": true
}
```

#### PATCH "/movies/{movie_id}"
- Updates the movie with the ID "movie_id"
- Request arguments: "title" string (optional), "release_date", formatted as YYYY-MM-DD (optional)
- Returns: a key "success" that equals true along with a key "movie" that contains the just-updated movie object as a dictionary inside an array
```
curl --location --request PATCH 'BASE_URL/movies/2' \
--header 'Authorization: Bearer JWT_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data-raw '{
    "release_date": "2023-02-22"
}'
```
```
{
    "movies": [
        {
            "id": 2,
            "release_date": "2023-02-22",
            "title": "Armageddon 2"
        }
    ],
    "success": true
}
```

## Testing
To run the test suite locally, first set the `DATABASE_URL` environment variable in `setup.sh` to a local postgres database. The run the following:

```
source setup.sh
python test_app.py
```