'use strict';


angular.module('eateratorApp')


.factory('localStorageService', function ($http){
    
    var getToken = function(){
    // getting token from url
         return $http.post('/auth/', JSON.stringify({ username: "msalii@ukr.net", password: "mSalii123!"})); 
        };
    return {
    getToken: getToken
  };
    
        
})

.factory('AuthInterceptor', function ($window, $q) {
    return {
        request: function(config) {
            config.headers = config.headers || {};
            config.headers.ContentType = 'application/json';
            if ($window.localStorage.getItem('id_token')) {
                config.headers.Authorization = 'Bearer ' + $window.localStorage.getItem('id_token');
            }
            return config || $q.when(config);
        },
        response: function(response) {
            if (response.status === 401) {
                // TODO: Redirect user to login page.
            }
            return response || $q.when(response);
        }
    };
})

// grab recipes from the server
.factory('recipesFactory', function($http){
    var allRecipes = [];
    return {
        searchRecipes: function(ingredientsPayload, numberOfRecipes){
            console.log(ingredientsPayload);
            numberOfRecipes = numberOfRecipes || 20
            return $http({
                method: 'POST',
                url: '/recipe/search/' + numberOfRecipes,
                data: ingredientsPayload
             })
        },
        getDetailedRecipe: function(recipePk) {
            return $http({
                method: "GET",
                url: '/recipe/recipe/' + recipePk
            })
        },
        getTopIngredients: function(numberOfTopIngredients) {
            numberOfTopIngredients = numberOfTopIngredients || 15;
            return $http({
                method: "GET",
                url: '/recipe/top-ingredients/' + numberOfTopIngredients
            })
        },
        getRelatedIngredient: function(ingredient, numberOfRelatedIngredients){
            numberOfRelatedIngredients = numberOfRelatedIngredients || 10;
            // encodeURIComponent just replaces spaces with %20 for making valid url, allows inclusion of spaces in ingredient
            ingredient = encodeURIComponent(ingredient.trim())
            return $http({
                method: "GET",
                url: '/recipe/related_ingredients/' + ingredient + '/' + numberOfRelatedIngredients
            })
        }
    }
})

.factory('userFactory', function($http){
    return {
        getUserFavouriteRecipes: function(maximumNumber) {
            maximumNumber = maximumNumber || 15;
            return $http({
                method: "GET",
                url: '/user/favourite-recipes/' + maximumNumber,
            })
        },
        getUserRecentSearches: function(maximumNumber) {
            maximumNumber = maxmimumNumber || 15;
            return $http({
                method: "GET",
                url: '/user/recent-searches/' + maxmimumNumber,
            })
        },
        addUserFavourite: function(recipePk) {
            return $http({
                method: "POST",
                url: '/user/favourite-recipe/' + recipePk
            })
        }
    }
})

// Register the previously created AuthInterceptor.
.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
})
    