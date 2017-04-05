'use strict';

angular.module('eateratorApp', [])

    .controller('MainCtrl',['$scope', 'localStorageService', 'recipesFactory', '$http', '$window', function($scope, localStorageService, recipesFactory, $http, $window){
        $scope.showDetails = false;
        $scope.showDescription = false;
            localStorageService.getToken().then(function(response){
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
            }
            )
            .catch(function(){
                console.log("ebites` konem");
            })
         
           $scope.searchRecipes = function(ingredients){
               $scope.ingredientsPayload = {
                    'ingredients': ingredients.name.split(",")
                }
                var request = recipesFactory.searchRecipes($scope.ingredientsPayload);
                request.then(function(response) {
                    // response.data is already parsed into a JSON object, contains recipe format from documentation
                    console.log(response.data);
                    console.log(response.data.recipes);
                    return $scope.searchedRecipes = response.data.recipes || [];
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
    }
    ])
    