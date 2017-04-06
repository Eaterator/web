'use strict';

angular.module('eateratorApp')
.controller('AppCtrl',
    ['$scope', 'authenticationService', '$http', '$window', '$state', '$stateParams',
    function($scope, authenticationService, $http, $window, $state, $stateParams){
        $scope.token = $window.localStorage.getItem("id_token") || '';
        if ($scope.token == '') {
            console.log($state.params);
            $scope.token = $state.params.access_token || '';
            if ($scope.token != '') {
                $window.localStorage.setItem('id_token', $scope.token);
                $state.go('search');
            }
        }
        $scope.isLoggedIn = function() {
            return !($scope.token === '' || $scope.token === null) || $scope.token === undefined;
        }
        $scope.refreshToken = function() {
            if ($scope.isLoggedIn()) {
                var request = authenticationService.refreshToken();
                request.then(function(response){
                    $scope.token = response.data.access_token;
                    $window.localStorage.setItem("id_token", $scope.token);
                    if ($state.current.name == 'login') {
                        $state.go('search');
                    }
                }).catch(function(){
                    $scope.token = '';
                    $window.localStorage.removeItem('id_token');
                    $state.go('login');
                });
            } else {
                if ($state.current.name != 'about' && $state.current.name != 'contact' && $state.current.name != 'home'){
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
        $scope.ingredients = [];
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

       $scope.getPopularIngredients = function() {
            var request = recipesFactory.getPopularIngredients();
            request.then(function(response) {
                $scope.popularIngredients = response.data.ingredients;
            }).catch(function(){
                console.log("Error getting popular ingredients")
            })
       }

       $scope.addPopular = function(idx) {
            var item = $scope.popularIngredients[idx];
            $scope.popularIngredients.splice(idx, 1);
            $scope.ingredients.push({
                text: item.name
            });
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

        $scope.addFavourite = function(idx, recipe) {
            var request = userFactory.addUserFavourite(recipe.pk);
            $scope.searchedRecipes[idx].favourite = true;
            return;
        }

        $scope.removeFavourite = function(idx, recipe) {
            var _ = userFactory.deleteUserFavourite(recipe.pk);
            $scope.searchedRecipes[idx].favourite = false;
            return;
        }

        $scope.getPopularIngredients();
    }
])
.controller('AuthCtrl',
    ['$scope', 'authenticationService', 'recipesFactory', '$http', '$window', '$state', '$stateParams',
    function($scope, authenticationService, recipesFactory, $http, $window, $state, $stateParams){

        if ($scope.accessToken != ''){
            $state.go('login');
        }
        $scope.registerData = {}
        $scope.isRegistering = false;
        $scope.errors = {}
        $scope.username = '';
        $scope.password = '';

        $scope.login = function() {
            var request = authenticationService.getToken()
            request.then( function(response) {
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
                $state.go('search')
            }).catch( function(){
                console.log("ebites konem")
            });
        }

        $scope.socialLogin = function(provider) {
            if (provider == 'facebook'){
                var request = authenticationService.socialLoginFacebook()
            }
            if (request === null || request === undefined) {
                return;
            }
            request.then(function(response){
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
                $state.go('home');
            }).catch(function(error){
                console.log("social error");
                console.log(error);
            })
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
    function ($scope, userFactory, recipesFactory, $http, $window) {

        $scope.getUserRecentSearches = function(number) {
            number = number || 20;
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
                var searchedRecipes = response.data.recipes || [];
                searchedRecipes = recipesFactory.setDefaultImageIfEmpty(searchedRecipes);
                $scope.searchedRecipes = searchedRecipes;
                // Set as favourite so that the standard recipe view works
                for (var i = 0; i < $scope.searchedRecipes.length; i++) {
                    $scope.searchedRecipes[i].favourite = true;
                }
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

        // TODO better solution to this? Duplicate Methods from recipeController
        // It may be better to re-use RecipeCtrl and somehow changed some settings
        // via $stateParams
        $scope.showDetails = false;
        $scope.showDescription = false;

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

        $scope.removeFavourite = function (idx, recipe) {
            var request = userFactory.deleteUserFavourite(recipe.pk)
            request.then(function(response){
                $scope.searchedRecipes.splice(idx, 1);
                console.log("Success!");
            }).catch(function() {
                console.log("Error!");
            });
        }

    }
])
.controller('AdminCtrl',
    ['$scope', 'authenticationService', 'adminFactory', '$http', '$window', '$filter',
    function($scope, authenticationService, adminFactory, $http, $window, $filter){
    }
]);
    