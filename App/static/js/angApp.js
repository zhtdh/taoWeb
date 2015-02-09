/**
 * Created by Administrator on 2015/1/15.
 */
var myApp = angular.module('blacapp', ['ui.router', 'blac-util']);

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


myApp.controller("angIndex", function($scope, blacAccess, blacPage){
  var lp = $scope;
  console.log("ffffeeeeeeeef");
  function getForeCol( aKind , aParentId, aCallback ) {
    var l_param = { kind: aKind , parentId: aParentId};
    console.log("akind " , aKind);
    //if (aParentId.length > 1) l_param.parentId = aParentId;
    blacAccess.getForeCol(l_param)
      .then(function (aRtn) {
        console.log(JSON.stringify(aRtn) );
        aCallback(null, aRtn);
      },
      function (err) {
        console.log(JSON.stringify(err));
        aCallback(JSON.stringify(err), null);
      }
    );
  };

  lp.psContentInfo = { pageCurrent: 1, pageRows: 10, pageTotal: 0  }; // init;
  lp.contentList = []; // article list
  function psGetContent(aOffset, aParentKind, aKind, aParentId, aId, aHasContent ) {
    if (!aId) aId = "";
    if (!aParentId) aParentId = "";
    if (!aParentKind) aParentKind = [];
    if (!aHasContent) aHasContent = 1;

    blacPage.psGetContent(blacAccess.getForeArt,
      [lp.psContentInfo, aParentKind, aKind , aParentId, aId, aHascontent], aOffset
      ,function(aErr, aRtn){
        lp.contentList = aRtn.exObj.userList;
        lp.psContentInfo = aRtn.psInfo;
        lp.contentHasLast = (lp.psContentInfo.pageCurrent == lp.psContentInfo.pageTotal)?false:true;
        lp.contentHasPrior = (lp.psContentInfo.pageCurrent == 1)?false:true;
        if (lp.contentList) blacAccess.setDataState(lp.contentList, blacAccess.dataState.clean); else lp.contentList = [];
      });
  };


  lp.getNav = function() { console.log("fffff");  getForeCol([',nav0,'], "") };
  lp.getArt = function() { console.log("get art");
    psGetContent(1, [], [], 'C67743685CF00001FFEB15602B167D') };

  lp.ngNavList = []
  getForeCol([',nav0,'], "", function(aErr, aRtn){
    if (aRtn) lp.ngNavList = aRtn.exObj.contentList;
    $.each(lp.ngNavList, function(aIdx, aVal){
      getForeCol([',sub-nav,'], aVal.id, function(aErr, aRtn){
        if (aRtn)
          if (aRtn.exObj.contentList.length > 0 )  lp.ngNavList[aIdx].submenu = aRtn.exObj.contentList;
      })
    });
  })


});


myApp.controller("angIndex", function($scope, blacAccess, blacPage){
  var lp = $scope;
  function getForeCol( aKind , aParentId, aCallback ) {
    var l_param = { kind: aKind , parentId: aParentId};
    console.log("akind " , aKind);
    //if (aParentId.length > 1) l_param.parentId = aParentId;
    blacAccess.getForeCol(l_param)
      .then(function (aRtn) {
        console.log(JSON.stringify(aRtn) );
        aCallback(null, aRtn);
      },
      function (err) {
        console.log(JSON.stringify(err));
        aCallback(JSON.stringify(err), null);
      }
    );
  };

  lp.psContentInfo = { pageCurrent: 1, pageRows: 10, pageTotal: 0  }; // init;
  lp.contentList = []; // article list
  function psGetContent(aOffset, aParentKind, aKind, aParentId, aId, aHasContent ) {
    if (!aId) aId = "";
    if (!aParentId) aParentId = "";
    if (!aParentKind) aParentKind = [];
    if (!aHasContent) aHasContent = 1;

    blacPage.psGetContent(blacAccess.getForeArt,
      [lp.psContentInfo, aParentKind, aKind , aParentId, aId, aHascontent], aOffset
      ,function(aErr, aRtn){
        lp.contentList = aRtn.exObj.userList;
        lp.psContentInfo = aRtn.psInfo;
        lp.contentHasLast = (lp.psContentInfo.pageCurrent == lp.psContentInfo.pageTotal)?false:true;
        lp.contentHasPrior = (lp.psContentInfo.pageCurrent == 1)?false:true;
        if (lp.contentList) blacAccess.setDataState(lp.contentList, blacAccess.dataState.clean); else lp.contentList = [];
      });
  };


  lp.getNav = function() { console.log("fffff");  getForeCol([',nav0,'], "") };
  lp.getArt = function() { console.log("get art");
    psGetContent(1, [], [], 'C67743685CF00001FFEB15602B167D') };

  /*
  lp.ngNavList = []
  getForeCol([',nav0,'], "", function(aErr, aRtn){
    if (aRtn) lp.ngNavList = aRtn.exObj.contentList;
    $.each(lp.ngNavList, function(aIdx, aVal){
      getForeCol([',sub-nav,'], aVal.id, function(aErr, aRtn){
        if (aRtn)
          if (aRtn.exObj.contentList.length > 0 )  lp.ngNavList[aIdx].submenu = aRtn.exObj.contentList;
      })
    });
  })
  */

});