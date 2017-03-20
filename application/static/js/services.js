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

// Register the previously created AuthInterceptor.
.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
});
    
    