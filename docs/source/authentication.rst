#########################
Authentication Module API
#########################
Module that handles authentication for users, using social logins or standard username/password combinations. After login in all routes return a JWT in the response body. This token must be passed into subsequent requests where authentication is required, otherwise, and unauthorized (code 403) is returned. In the case where the route is stricted to a user type in the token (i.e. admin verse business verse regular), and unauthorized code is returned (code 403). All endpoints begin with `/auth`.

Protected Endpoints
-------------------
Endpoints that require authentication need an access token (JWT) in the header. The header needs to be formatted like:

.. code-block:: none
		
    "Authorization: Bearer ccccc.cccccccccccc.ccccc"

Where the `cccccc.cccccccccccccccccc.ccccc` is the value returned as the "access_token" field in the body of the successful `/auth` endpoints outlined below. 

Standard Login
--------------
Standard login uses a submitted username/password combination and checks with the registered username/password combination. If there is no username and/or password error, an unauthorzed (403) code is returned.

.. code-block:: none
		
    endpoint = '/auth/'
    request = {"username": "myusername", "password": "mypassword"}
    response = {"access_token": "cccccc.ccccccccccccccccc.cccc"}
    error = 400 (bad request), username and/or password fields do not exist in request
    error = 403 (unauthorized), username/password mismatch, or password wrong

Register User
-------------
Endpoint to register a new user with the standard username/password login procedure, along with user information.

.. code-block:: none

    endpoint = '/auth/register'
    request =
    {
        "username":       "myusername",
	"password":       "mypassword",
	"confirm":        "mypassword",
	"email":          "my@email.com",
	"date_of_birth":  "1991-01-01",
	"first_name":     "new",
	"last_name":      "user"
    }
    response = {"access_token": "cccccc.ccccccccccccccc.ccccc"}
    error = 400 form data could not be validated/missing
    error = 403 unauthorized, username is taken

Social Login
------------
Social login only supports facebook right now, with a login route for the iOS/Android app and the web application.

Web App Social Login
--------------------
Redirects to the OAuth provider (i.e. Facebook) for a login. Registers them if there is a successful OAuth login and the social ID from the provider does not exist as a user in the database. 

.. code-block:: none
		
    Endpoint = '/auth/callback/<provider>'  # provider = 'facebook' only right now
    Response = {"access_code": "ccccc.cccccccccccccc.cccc"}
    Error = 400 BAD REQUEST, provider does not exist
    Error = 403 UNAUTHORIZED, error with OAuth login procedure

iOS/Android Login
-----------------
Takes a token from the app from an OAuth login. The route verifies the token with the provider and then registers a new user with the given social id if they do not exist.

.. code-block:: none
		
    Endpoint = '/auth/app/<provider>'  # provider = 'facebook' only right now
    Repsonse = {"access_code": "ccccccccc.ccccccccccccccccc.cccccccccccc"}
    Error = 400 BAD REQUEST OAuth provider does not exist
    Error = 403 UNAUTHORIZED, invalid OAuth token submitted, could not be verified


