'use strict';

//angular.module('eateratorApp')
  //  .constant("baseURL", "http://localhost:5000")

var app = angular.module('eateratorApp', []);

app.factory('localStorageService', ['$scope', function ($scope){
    
         $http.get('/auth/authorize/facebook')      
               .success(function(data, status, headers, config){
                    var authToken = data.access_token; // probably just token
                })
                .error(function(data, status, headers, config){
                    // error handler
                });
    
        return authToken;
    
}]);
    
    