################
Users Module API
################
These API endpoints allow for user data to be persisted/queried. Right now, it keeps track of user searchs, and users' favourite recipes. All requests require a JWT token.

.. code-block:: none

	"Authorization" => "Bearer ccccccc.ccccccccccc.cccccccc"

Get User Favourite Recipes
--------------------------
Returns a list of a user's favourite recipes. Note that the request is just a list but I will include tags. The return response will be in the same format as the recipe search to keep parsing of reponses consistent. 

.. code-block:: none

	Endpoint = '/user/favourite-recipes'
	Response = {
		"recipes" : [
		    [
                        6442, 
                        "Turkey Saut\u00e9 with Fresh Cherry Sauce recipe | Epicurious.com"
                    ], 
                    [
                        6904, 
                        "Kirsch and Tart Cherry Souffles recipe | Epicurious.com"
                    ]

		]
	}

User Searches
-------------
Returns a list of recent user searches ordered by date they were searched.

.. code-block:: none

	Method       = "GET"
	Endpoint     = '/user/recent-searches/<num_searches:int>
	num-searches = number of searches to return
		default: 10
		maximum: 40
	Response     = {
		        "searches": [
		            ["ingredient", "ingredient", "ingredient"]
		        ]
	               }
	Error 401 = UNAUTHORIZED (401), invalid, expired, or missing JWT token

Add User Favourite
------------------
Registers a favourite recipe for a given user. Requires a JWT token.

.. code-block:: none

	Method = "POST"
	Endpoint = '/user/favourite/<recipe_id:int>'
	recipe_id = id for a recipe to favourite
	Response = {"message": "OK"}
	Error 400 = BAD REQUEST, no recipe_id provided, or it could not be parsed to int
