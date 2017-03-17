'use strict';


var app = angular.module('eateratorApp', []);
app.controller('MainCtrl', 'localStorageService', function($scope, $localStorageService, $http, $window){

        $scope.token = localStorageService;
               
               
  //          $scope.submit = function() {
  //           localStorage.setItem('id_token', authToken);
  //           fbToken = localStorage.getItem('id_token');
  //           
  //           $http.post('/auth/callback/facebook', fbToken, {"auth": fbToken})
  //              .then(function(response){
  //              //sucess
  //              //response contains auth token
  //              // localStorage.setItem("authToken", response.token);
  //              }, function(response){
  //                  //error
  //              });  
  //       }
})