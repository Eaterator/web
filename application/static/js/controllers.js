'use strict';

angular.module('eateratorApp', [])

    .controller('MainCtrl',['$scope', 'localStorageService', '$http', '$window', function($scope, localStorageService, $http, $window){
        $scope.showDescription = false;
            localStorageService.getToken().then(function(response){
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
            }
            )
            .catch(function(){
                console.log("ebites` konem");
            });

                           
                           
            //$scope.checkField = function($event){
            //    if($scope.showDescription == false){
            //        $scope.showDescription = true;
            //    }
            //    else if($scope.showDescription == true){
            //        $scope.showDescription = false;
            //    }
            //    return $scope.showDescription;
            //} 
    }
    ])
    