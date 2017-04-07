//'use strict';
//
var app = angular.module('eateratorApp', ['ui.router', 'ngTagsInput'])
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
.config(
    ['$stateProvider', '$urlRouterProvider', '$locationProvider',
    function ($stateProvider, $urlRouterProvider, $locationProvider) {

        $locationProvider.html5Mode({
          enabled: true,
        });

        $urlRouterProvider.otherwise('/search');

        $stateProvider
            .state('index', {
                url: '/?access_token={accessToken}',
                controller: function($scope, $state) {
                    console.log($state.params);
                    $state.go('search', {'access_token': $state.params.access_token})
                }
            })
            .state('search', {
                url: '/search?access_token={accessToken}',
                views: {
                    '': {
                        controller: 'AppCtrl'
                    },
                    'header@search': {
                        templateUrl: 'carousel.html'
                    },
                    'content@search': {
                        templateUrl: 'search.html',
                        controller: 'RecipeCtrl'
                    }
                },
            })
            .state('login', {
                url: '/login',
                views: {
                    '': {
                        controller: 'AppCtrl'
                    },
                    'header@login': {
                        templateUrl: 'carousel.html'
                    },
                    'content@login': {
                        templateUrl: '/auth/login.html',
                        controller: 'AuthCtrl'
                    }
                }
            })
            .state('user', {
                url: '/user',
                views: {
                    '': {
                        controller: "AppCtrl"
                    },
                    'content@user': {
                        templateUrl: '/user/dashboard.html',
                        controller: 'UserCtrl'
                    }
                }
            })
            .state('admin', {
                url: '/admin',
                views: {
                    '': {
                        controller: "AppCtrl"
                    },
                    'content@admin': {
                        templateUrl: '/admin/index.html',
                        controller: 'AdminCtrl'
                    }
                }
            })
            .state('about', {
                url: '/about',
                views: {
                    '': {
                        controller: "AppCtrl"
                    },
                    'content@about': {
                        templateUrl: '/about.html',
                    }
                }
            })
            .state('contact', {
                url: '/contact',
                views: {
                    '': {
                        controller: "AppCtrl"
                    },
                    'content@contact': {
                        templateUrl: '/contact.html',
                    }
                }
            })
    }]
);

//app.config(['$qProvider', function ($qProvider) {
//    $qProvider.errorOnUnhandledRejections(false);
//}]);
