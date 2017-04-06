'use strict';

angular.module('eateratorApp')
.controller('AppCtrl',
    ['$scope', 'authenticationService', '$http', '$window', '$state',
    function($scope, authenticationService, $http, $window, $state){
        $scope.token = $window.localStorage.getItem("id_token");
        console.log($state);
        $scope.isLoggedIn = function() {
            return !($scope.token === '' || $scope.token === null) || $scope.token === undefined;
        }

        $scope.refreshToken = function() {
            console.log($scope.isLoggedIn());
            console.log($scope.token);
            if ($scope.isLoggedIn()) {
                var request = authenticationService.refreshToken();
                request.then(function(response){
                    $scope.token = response.data.access_token;
                    $window.localStorage.setItem("id_token", $scope.token);
                }).catch(function(){
                    $scope.token = '';
                    $window.localStorage.removeItem('id_token');
                    $state.go('login')
                });
            } else {
                if ($state.current.name != 'about' && $state.current.name != 'contact'){
                    $state.go('login');
                }
            }
        }

        $scope.logout = function() {
            $window.localStorage.removeItem('id_token');
            $scope.token = '';
            $state.go('login')
        }

        $scope.refreshToken();
    }
])
.controller('RecipeCtrl',
    ['$scope', 'authenticationService', 'userFactory', 'recipesFactory', '$http', '$window', '$filter',
    function($scope, authenticationService, userFactory, recipesFactory, $http, $window, $filter){
        // Controller setup
        $scope.showDetails = false;
        $scope.showDescription = false;
        $scope.token = $window.localStorage.getItem('id_token');
         
        $scope.searchRecipes = function(ingredients){
            var payload = [];
            for (var i = 0; i < ingredients.length; i++) {
                payload.push(ingredients[i].text);
            }
            $scope.ingredientsPayload = {
                'ingredients': payload
            }
            console.log($scope.ingredientsPayload);
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

        $scope.addFavourite = function(recipePk) {
            var _ = userFactory.addUserFavourite(recipePk);
        }

        $scope.removeUserFavourite = function(recipePk) {
            var _ = userFactory.deleteUserFavourite(recipePk);
        }
    }
])
.controller('AuthCtrl',
    ['$scope', 'authenticationService', 'recipesFactory', '$http', '$window', '$state',
    function($scope, authenticationService, recipesFactory, $http, $window, $state){
        $scope.registerData = {}
        $scope.isRegistering = false;
        $scope.errors = {}
        $scope.username = '';
        $scope.password = '';

        $scope.login = function() {
            var request = authenticationService.getToken()
            request.then( function(response) {
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token), $scope.token;
                $scope.hideLoginDisplay = true;
                $state.go('home')
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
                $state.go('home')
            }).catch(function(response){
                $scope.errors.register = response.data;
            })
        }
    }
])
.controller('UserCtrl',
    ['$scope', 'userFactory', 'recipesFactory', '$http', '$window',
    function ($scope, userFactory, recipeFactory, $http, $window) {

        $scope.getUserRecentSearches = function(number) {
            number = number || 20;
            console.log(number);
            var request = userFactory.getUserRecentSearches(number);
            request.then(function (response){
                $scope.userSearches = response.data;
            }).catch(function() {
                $scope.userSearches = [];
            });
        }

        $scope.getUserFavouriteRecipes = function(number) {
            number = number || 20;
            var request = userFactory.getUserFavouriteRecipes(number);
            request.then(function (response){
                $scope.searchedRecipes = response.data;
            }).catch(function() {
                $scope.searchedRecipes = [];
            })
        }

        $scope.repeatSearch = function(search) {
            var request = recipesFactory.searchRecipes(search);
            request.then(function(response){
                $scope.searchedRecipes = response.data;
            }).catch(function() {
                $scope.searchRecipes = [];
            })
        }

        $scope.getUserFavouriteRecipes();
        $scope.getUserRecentSearches();

    }
])
.controller('AdminCtrl',
    ['$scope', 'authenticationService', 'adminFactory', '$http', '$window', '$filter',
    function($scope, authenticationService, adminFactory, $http, $window, $filter){
    }
]);
    