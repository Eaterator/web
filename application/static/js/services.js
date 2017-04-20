'use strict';


angular.module('eateratorApp')

.factory('authenticationService', function ($http, $window){

    var decodeJWT = function(token) {
        // decodes from base 64 string
        var token = $window.localStorage.getItem('id_token');
        var encoded = token.split('.')[1];
        var output = encoded.replace('-', '+').replace('_', '/');
        switch (output.length % 4) {
           case 0:
               break;
           case 2:
               output += '==';
               break;
           case 3:
               output += '=';
               break;
           default:
               throw 'Illegal base64url string!';
        }
        return window.atob(output);
    };

    var getTokenClaims = function(token) {
        var claims = {};
            if (typeof token != 'undefined') {
                claims = JSON.parse(decodeJWT(token));
            }
        return claims;
    };

    return {
        getToken: function(username, password){
            // getting token from url
            var user = username || "msalii@ukr.net";
            var pass = password || "mSalii123!";
            return $http({
                url:  '/auth/',
                method: "POST",
                data: JSON.stringify({ username: user, password: pass})
            });
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
            $window.location.href = "/auth/authorize/facebook";
        },
        isAdmin: function(token) {
            var claims = getTokenClaims(token);
            return claims.user_claims.role == 'admin';
        },
        tokenNeedsRefresh: function(token){
            var claims = getTokenClaims(token);
            // return true if token will expire in 1 week (7 days);
            return (new Date(claims.exp * 1000) - new Date().getTime()) <= 1000*60*60*24*7;
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
            numberOfRecipes = numberOfRecipes || 20;
            return $http({
                method: 'POST',
                url: '/recipe/v2/search/' + numberOfRecipes,
                data: ingredientsPayload
             });
        },
        getDetailedRecipe: function(recipePk) {
            return $http({
                method: "GET",
                url: '/recipe/recipe/' + recipePk
            });
        },
        getTopIngredients: function(numberOfTopIngredients) {
            numberOfTopIngredients = numberOfTopIngredients || 15;
            return $http({
                method: "GET",
                url: '/recipe/top-ingredients/' + numberOfTopIngredients
            });
        },
        getRelatedIngredient: function(ingredient, numberOfRelatedIngredients){
            numberOfRelatedIngredients = numberOfRelatedIngredients || 10;
            // encodeURIComponent just replaces spaces with %20 for making valid url, allows inclusion of spaces in ingredient
            ingredient = encodeURIComponent(ingredient.trim());
            return $http({
                method: "GET",
                url: '/recipe/related_ingredients/' + ingredient + '/' + numberOfRelatedIngredients
            });
        },
        getPopularIngredients: function() {
            return $http({
                method: "POST",
                url: '/recipe/top-ingredients'
            });
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
            });
        },
        getUserRecentSearches: function(maximumNumber) {
            maximumNumber = maximumNumber || 15;
            return $http({
                method: "GET",
                url: '/user/recent-searches/' + maximumNumber,
            });
        },
        addUserFavourite: function(recipePk) {
            return $http({
                method: "POST",
                url: '/user/favourite-recipe/' + recipePk
            });
        },
        deleteUserFavourite: function(recipePk) {
            return $http({
                method: "POST",
                url: '/user/favourite-recipe/delete/' + recipePk
            });
        }
    }
})

.factory('adminFactory', function($http){

    var getDateNDaysAgo = function(N) {
        var today = new Date();
        var priorDate = new Date(new Date().setDate(today.getDate()-N));
        return priorDate.toISOString().split('T')[0];
    };

    return {
        getNewUsers: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            startDate = startDate || getDateNDaysAgo(30);
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/admin/statistics/search/new-users/" + startDate +"/" + groupBy
            });
        },
        getTotalUserSearches: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            startDate = startDate || getDateNDaysAgo(30);
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/admin/statistics/search/" + startDate + "/" + groupBy
            });
        },
        getUniqueUserSearches: function(startDate, groupBy) {
            // :param startData: date of earliest searches
            // :param groupBy: group searches by total per DAY || MONTH
            startDate = startDate || getDateNDaysAgo(30);
            groupBy = groupBy || 'DAY';
            return $http({
                method: "GET",
                url: "/admin/statistics/search/unique-users/" + startDate + "/" + groupBy
            });
        },
        getPopularIngredients: function() {
            return $http({
                method: "GET",
                url: '/admin/statistics/search/popular-ingredients'
            });
        }
    };
})

// Register the previously created AuthInterceptor.
.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
})
    
