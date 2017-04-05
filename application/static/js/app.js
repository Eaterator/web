//'use strict';
//
var app = angular.module('eateratorApp', [])
.filter('ingredientFormatter', function() {
    return function(ingredient) {
        var displayString = '';
        if (ingredient.ingredient.amount != '') {
            displayString += ingredient.ingredient.amount.toFixed(2);
            if (ingredient.ingredient.unit != '') {
                displayString += ' ' + ingredient.ingredient.unit;
            }
            if (ingredient.ingredient.amount > 1 && ingredient.ingredient.unit != '') {
                displayString += 's '+
                    ingredient.ingredient.modifier + " " +
                    ingredient.ingredient.name;
            } else {
                displayString += ' ' +
                    ingredient.ingredient.modifier + " " +
                    ingredient.ingredient.name;
            }
        } else {
            displayString += ingredient.ingredient.modifier + " " +
                    ingredient.ingredient.name;
        }
        return displayString;
    }
})
//.config(['$qProvider', function ($qProvider) {
//    $qProvider.errorOnUnhandledRejections(false);
//}]);
// 
//app.config(['$routeProvider', function ($routeProvider) {
//
//    $routeProvider
//        .when('/', {
//            controller: 'MainCtrl'
//            //templateUrl: '../../templates/base.html'
//        })
// 
// 
//        .otherwise({ redirectTo: '/' });
//}])

//app.config(['$qProvider', function ($qProvider) {
//    $qProvider.errorOnUnhandledRejections(false);
//}]);