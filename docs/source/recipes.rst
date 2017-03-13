#################
Recipe Module API
#################
The recipes API focuses solely on searching the database for recipes for regular and business users.

Required Authentication Headers
-------------------------------
All requests need an authentication token as a header in the request in order to complete a search.

.. code-block:: none

	"Authorization" => "Bearer ccccccccc.ccccccccccccccccc.ccccccc"

Regular User Endpoints
----------------------

Regular users can submit a list of ingredients to complete a search, which returns a list of recipes with their titles. I will eventually include a score/rating field as well. It will automatically log the user search into the appropriate table for use with the `user` module to query/collect user data.

**N.B. minimum ingredient number is 3 (i.e. length(ingredients) >= 3)**

**N.B that I will label response fields (i.e. "id": 4567, "title": "Recipe Title")**

.. code-block:: none
		
	Method = "GET"
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
                        "title": "Turkey Saut\u00e9 with Fresh Cherry Sauce recipe | Epicurious.com"
                    }, 
                    {
                        "pk": 6904, 
                        "title": "Kirsch and Tart Cherry Souffles recipe | Epicurious.com"
                    }

		]
	}
	Error 400 = BAD REQUEST, not enough ingredients
	Error 401 = UNAUTHORIZED, invalid or expired token, or non existant token in header

Business User Endpoints
-----------------------
Business search has both single and batch search options. Single search is identical to the user search above, put has a different endpoint. Note that requests from business users to the regular user endpoints will be denied with a FORBIDDEN (403) code.

.. code-block:: none

	Method = "GET"
	Endpoint = '/recipe/search/business'
	Endpoint = '/recipe/search/business/<limit:int>'
	limit = search param for number to return
		default: 20
		maximum: 250

Batch Search
------------
Allows a business user to input multiple searches in a single request. Note, this is not implemented yet!
