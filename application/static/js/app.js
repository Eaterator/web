//'use strict';
//
var app = angular.module('eateratorApp', []);
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

app.config(['$qProvider', function ($qProvider) {
    $qProvider.errorOnUnhandledRejections(false);
}]);