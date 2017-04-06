'use strict';


angular.module('eateratorApp')

.factory('authenticationService', function ($http, $window){
    var clientId = '647922095392507';
    return {
        getToken: function(){
            // getting token from url
            return $http.post('/auth/', JSON.stringify({ username: "msalii@ukr.net", password: "mSalii123!"}));
        },
        registerUser: function(registerPayload){
            return $http({
                method: "POST",
                url: '/auth/register',
                data: registerPayload
            });
        },
        refreshToken: function(token) {
            return $http({
                method: "GET",
                url: '/auth/refresh',
            });
        },
        socialLoginFacebook: function() {
            return $window.location.href = "/auth/authorize/facebook";
        }
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
    var defaultImage = "/static/images/default-recipe-pic.jpg";
    return {
        searchRecipes: function(ingredientsPayload, numberOfRecipes){
            console.log(ingredientsPayload);
            numberOfRecipes = numberOfRecipes || 20
            return $http({
                method: 'POST',
                url: '/recipe/v2/search/' + numberOfRecipes,
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
        },
        getPopularIngredients: function() {
            return $http({
                method: "POST",
                url: '/recipe/top-ingredients'
            })
        },
        setDefaultImageIfEmpty: function(searchRecipes) {
            for (var i = 0; i < searchRecipes.length; i++) {
                if (searchRecipes[i]["medium_img"] == '') {
                    searchRecipes[i]["medium_img"] = defaultImage;
                }
            }
            return searchRecipes;
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
            maximumNumber = maximumNumber || 15;
            return $http({
                method: "GET",
                url: '/user/recent-searches/' + maximumNumber,
            })
        },
        addUserFavourite: function(recipePk) {
            return $http({
                method: "POST",
                url: '/user/favourite-recipe/' + recipePk
            })
        },
        deleteUserFavourite: function(recipePk) {
            return $http({
                method: "POST",
                url: '/user/favourite-recipe/delete/' + recipePk
            })
        }
    }
})

.factory('adminFactory', function($http){
    return {
        newUserAnalytics: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/statistics/search/new-users/" + startDate +"/" + groupBy
            })
        },
        totalUserSearches: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/admin/statistics/" + startDate + "/" + groupBy
            });
        },
        uniqueSearchUsers: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/admin/statistics/search/unique-users/" + startDate + "/" + groupBy
            });
        }

    }
})

// Register the previously created AuthInterceptor.
.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
})
    