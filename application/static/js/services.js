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
    return{
        saveRecipes: function(parameter){
            console.log(parameter);
            return $http({
                method: 'POST',
                url: '/recipe/search',
                data: parameter
                //JSON.stringify({$params})
         }).then(function(response) {
                allRecipes = JSON.parse(response.data);
                consol.log(allRecipes);
                return allRecipes;
              })  
        },
        //getRecipes: function(){
        //    return $http({
        //        method: 'GET',
        //        url: '/recipe/search',
        //    }).then(function(response) {
        //        allRecipes = response.data;
        //        return allRecipes;
        //      }
        //)}
    }
})
    

// Register the previously created AuthInterceptor.
.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
})
    