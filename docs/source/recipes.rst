#################
Recipe Module API
#################
The recipes API focuses solely on searching the database for recipes for regular and business users.

Recipe Detail
=============
Get detailed information about a recipe.

.. code-block:: none

      Method = "GET"
      Endpoint = '/recipe/recipe/<pk:int>'
      Response = {
		"recipe": {
			"recipe": {
				    "pk": 1234
				    "title": "My great recipe"
				    "url": "http://foodnetwork.com.recipe/my-great-recipe
				    "average_rating": 3.4
				    "lowest_rating": 1
				    "count_rating": 34
				    "highest_rating": 4
				    "medium_img": "https://flickr.com/234243_m.jpg"
				    "thumbnail": "https://flickr.com/234243.jpb
				  },
			"ingredients": [
				    {
				      "ingredient": {
						      "name": "potato"
						      "modifier": "small"
						      "amount": 4
						      "unit": None
				                    }
				    }
			]
		}
	}


Recipe and Ingredient Search
============================

Regular User Endpoints
----------------------

Regular users can submit a list of ingredients to complete a search, which returns a list of recipes with their titles. I will eventually include a score/rating field as well. It will automatically log the user search into the appropriate table for use with the `user` module to query/collect user data.

**N.B. minimum ingredient number is 3 (i.e. length(ingredients) >= 3)**

.. code-block:: none
		
	Method = "POST"
	Endpoint = '/recipe/search'
	Endpoint = '/recipe/search/<limit:int>'
	limit = search param for number of recipes to return
		default: 20
		maximum: 100
	Request = {
		"ingredients": ["onions", "chicken", "red peppers"]
	}
	Response = {
		"recipes" : [
		    {
                        "pk": 6442, 
                        "title": "Turkey Saut\u00e9 with Fresh Cherry Sauce recipe | Epicurious.com",
                        "average_rating": 3.4,
                        "thumbnail": "https://flickr.com/image.jpg"
                    }, 
                    {
                        "pk": 6904, 
                        "title": "Kirsch and Tart Cherry Souffles recipe | Epicurious.com",
                        "average_rating": 4.2,
                        "thumbnail": https://flikr.com.image2.jpg"
                    }

		]
	}
	Error 400 = BAD REQUEST, not enough ingredients
	Error 401 = UNAUTHORIZED, invalid or expired token, or non existant token in header

Business User Endpoints
-----------------------
Business search has both single and batch search options. Single search is identical to the user search above, put has a different endpoint. Note that requests from business users to the regular user endpoints will be denied with a FORBIDDEN (403) code.

.. code-block:: none

	Method = "POST"
	Endpoint = '/recipe/search/business'
	Endpoint = '/recipe/search/business/<limit:int>'
	limit = search param for number to return
		default: 20
		maximum: 250

Batch Search
------------
Allows a business user to input multiple searches in a single request. Note, this is not implemented yet!

Ingredient Search
=================
These are a collection API endpoints to allow easier input of ingredients, and for users to explore related ingredients.

Top Ingredients
---------------
Envision to put this on the landing page so top ingredients are easy to click to input instead of typing.

.. code-block:: none
		
    Method = 'POST'
    Endpoint = '/top-ingredients/<limit:int>'
    limit = integer for number top ingredients to return
        default = 15
	maximum = 30
    Response = {
        'ingredients': [
	   {
            "name": "cream", 
            "pk": 3813
           }, 
           {
            "name": "parsley", 
            "pk": 3844
           }

	]
    }
    Error 401 = Unauthorized, no JWT supplied, or invalid/expired token.


Related Ingredient API
----------------------
Gives a list of related ingredients. URL will probably change an ingredient to a query string to avoid errors associated with spaces in ingredient names.

.. code-block:: none
		
    Method = 'POST'
    Endpoint = '/top-ingredients/<ingredient:string>/<limit:int>'
    ingredient = ingredient name to search for related ones
    limit = integer for number related ingredients to return
        default = 15
	maximum = 30
    Response = {
        'ingredients': [
	   {
            "name": "cream", 
            "pk": 3813
           }, 
           {
            "name": "parsley", 
            "pk": 3844
           }
	]
    }
    Error 401 = Unauthorized, no JWT supplied, or invalid/expired token.
    Error 400 = BAD REQUEST, no ingredient was supplied or could be parsed


