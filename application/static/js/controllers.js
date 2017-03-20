'use strict';

angular.module('eateratorApp', [])

// to fix iternal server error

    .controller('MainCtrl',['$scope', 'localStorageService', '$http', '$window', function($scope, localStorageService, $http, $window){

//        $scope.token = localStorageService;         
            localStorageService.getToken().then(function(response){
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
            }
            )
            .catch(function(){
                console.log("ebites` konem");
            });
        
            //$scope.login = function() {           
                //$scope.headers = AuthInterceptor; 
         //}
}])