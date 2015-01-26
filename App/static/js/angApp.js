/**
 * Created by Administrator on 2015/1/15.
 */
var myApp = angular.module('blacapp', ['ui.router']);

myApp.config(function($stateProvider, $urlRouterProvider) {
  //
  // For any unmatched url, redirect to /state1
  $urlRouterProvider.otherwise("/top");

  $stateProvider
    .state('top', {
      url: "/top",
      templateUrl: "partials/top.html"
    })
    .state('top.list', {
      url: "/list",
      templateUrl: "partials/toplist.html",
      controller: function($scope) {
        $scope.items = ["A", "List", "Of", "Items"];
      }
    })
    .state('sec', {
      url: "/sec",
      templateUrl: "partials/sec.html"
    })
    .state('sec.list', {
      url: "/list",
      templateUrl: "partials/seclist.html",
      controller: function($scope) {
        $scope.things = ["A", "Set", "Of", "Things"];
      }
    })
    .state('thi', {
      url: "/thi",
      templateUrl: "partials/thi.html"
    })
    .state('thi.list', {
      url: "/list",
      templateUrl: "partials/thilist.html",
      controller: function($scope) {
        $scope.things = ["A33", "S33", "Of3", "3Things"];
      }
    }).state('fou', {
      url: "/fou",
      templateUrl: "partials/fou.html"
    })
    .state('fou.list', {
      url: "/list",
      templateUrl: "partials/foulist.html",
      controller: function($scope) {
        $scope.things = ["A4", "Set44", "Of44", "Things44"];
      }
    }).state('fiv', {
      url: "/fiv",
      templateUrl: "partials/fiv.html"
    })
    .state('fiv.list', {
      url: "/list",
      templateUrl: "partials/fivlist.html",
      controller: function($scope) {
        $scope.things = ["A5", "Set5", "Of5", "Things5"];
      }
    }).state('last', {
      url: "/last",
      templateUrl: "partials/last.html"
    })
    .state('last.list', {
      url: "/list",
      templateUrl: "partials/lastlist.html",
      controller: function($scope) {
        $scope.things = ["last", "last", "last", "Tlastgs5"];
      }
    })
});