'use strict';

angular.module('eateratorApp', [])

    .controller('MainCtrl',['$scope', 'localStorageService', 'recipesFactory', '$http', '$window', function($scope, localStorageService, recipesFactory, $http, $window){
        $scope.showDescription = false;
            localStorageService.getToken().then(function(response){
                $scope.token = response.data.access_token;
                $window.localStorage.setItem('id_token', $scope.token);
            }
            )
            .catch(function(){
                console.log("ebites` konem");
            })
         
             
           //recipesFactory.getRecipes().then(function(recipes){
           //    $scope.allRecipes = allRecipes;
           //})
           //
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
           
        
        //recipesFactory.getRecipes().then(function(response){
            //    $scope.recipes = {
            //        'title': 'response.recipes.title',
            //        'pk': 'response.recipes.pk'
            //    };
            //})
            //.catch(function(){
            //    console.log("kill me please");
            //});
        
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
    