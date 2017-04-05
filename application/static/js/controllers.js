'use strict';

angular.module('eateratorApp')
.controller('MainCtrl',
    ['$scope', 'authenticationService', 'recipesFactory', '$http', '$window', '$filter',
    function($scope, authenticationService, recipesFactory, $http, $window, $filter){
        // Controller setup
        $scope.showDetails = false;
        $scope.showDescription = false;
        $scope.registerData = {}
        $scope.isRegistering = false;
        $scope.errors = {}
        $scope.username = '';
        $scope.password = '';
        $scope.token = $window.localStorage.getItem('id_token');
        // TODO validate token here to make sure it is not expired
         
       $scope.searchRecipes = function(ingredients){
           $scope.ingredientsPayload = {
                'ingredients': ingredients.name.split(",")
            }
            var request = recipesFactory.searchRecipes($scope.ingredientsPayload);
            request.then(function(response) {
                // response.data is already parsed into a JSON object, contains recipe format from documentation
                console.log(response.data);
                console.log(response.data.recipes);
                var searchedRecipes = response.data.recipes || [];
                searchedRecipes = recipesFactory.setDefaultImageIfEmpty(searchedRecipes);
                $scope.searchedRecipes = searchedRecipes;
                return;
            })
       }

       $scope.getDetailedRecipe = function(pk){
           var requestDetails = recipesFactory.getDetailedRecipe(pk);
                requestDetails.then(function(response){
                    console.log(response.data.recipe.ingredients);
                    return $scope.searchedDetails = response.data.recipe.ingredients || [],
                    $scope.detailPk = response.data.recipe.recipe.pk;
                })
       }

        $scope.toggleDetails = function() {
            $scope.showDetails = !$scope.showDetails;
            console.log($scope.showDetails);
        };

        // get position of clicked recipe
        $scope.doClick = function($event){
            $scope.x = $event.clientX;
            $scope.y = $event.height;
            $scope.offsetX = $event.offsetX;
            $scope.offsetY = $event.pageY - 1400;
        };

        // Auth & login functions //
        $scope.isLoggedIn = function() {
            return !($scope.token === '' || $scope.token === null) || $scope.token === undefined;
        }

        $scope.refreshToken = function() {
            if ($scope.isLoggedIn()) {
                var request = authenticationService.refreshToken();
                request.then(function(response){
                    $scope.token = response.data.access_token;
                    $window.localStorage.setItem("id_token", $scope.token);
                }).catch(function(){
                    $scope.token = '';
                    $window.localStorage.removeItem('id_token');
                });
            }
        }

        $scope.logout = function() {
            $window.localStorage.removeItem('id_token');
            $scope.token = '';
            $scope.hideLoginDisplay = false;
        }

        $scope.login = function() {
            var request = authenticationService.getToken()
            request.then( function(response) {
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token), $scope.token;
                $scope.hideLoginDisplay = true;
            }).catch( function(){
                console.log("ebites konem")
            });
        }

        $scope.startRegistering = function() {
            $scope.isRegistering = true;
        }

        $scope.stopRegistering = function() {
            $scope.isRegistering = false;
        }

        $scope.register = function() {
            console.log($scope.registerData)
            var request = authenticationService.registerUser($scope.registerData);
            request.then(function(response){
                $scope.token = response.access_token;
                $window.localStorage.setItem("id_token", $scope.token);
            }).catch(function(response){
                $scope.errors.register = response.data;
            })
        }
        console.log($scope.token)
        $scope.refreshToken();
    }]);
    