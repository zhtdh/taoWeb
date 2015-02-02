/**
 * Created by blaczom@gmail.com on 2015/1/18.
 *
 * var app = angular.module('blacapp', ['blac-util']);
 * app.controller("ctrlXxx",function($scope,blacUtil) {
 *   blacUtil.createUUID()             : 生成uuid
 *   blacUtil.strDateTime(new Date())  : "2015-01-01 12:24" 格式化日期时间
 *   blacUtil.strDate(new Date())      : "2015-01-01" 格式化日期
 *   blacUtil.verifyBool(xxx)          : true / false 返回真假
 *   blacUtil.md5String(xxx)           : xxx  生成md5字符串
 *   blacUtil.shareCache = {global:{}} : 用于共享内容。
 *   blacUtil.event= { login: 'event:login' }
 *
 * app.controller("ctrlXxx",function($scope,blacStore) {
 *   blacStore.localRem(true)      : 无参数是读，有参数是写。 登录用户是否保存密码。
 *   blacStore.localUser('xx')     : 无参数是读，有参数是写。 登录用户
 *   blacStore.localWord('xx')     : 无参数是读，有参数是写。 登录用户是否保存密码。
 *   blacStore.getErr('xx')        : 得到错误记录。
 *   blacStore.setErr('xx')        : 无参数是清空错误记录。 有参数是设置
 *   blacStore.appendErr('xx')     : 添加错误记录。
 *   blacStore.customGet('key')        : 根据key得到对象
 *   blacStore.customSet('key', obj)   : 设置key对应的obj
 *
 * app.controller("ctrlXxx",function($scope,blacAccess) {
 *   blacAccess.httpQ(aUrl, aObject)  : 使用 httpQ('/rest',{func:'userlogin',ex_parm:{user:aObjUser}}).then(function(data){}, function(err){})
 *   blacAccess.userLoginQ(aObjUser)  : 使用 xxx().then(function(data){}, function(err){})
 *   blacAccess.
 *   blacAccess.
 */
angular.module('blac-util', ['angular-md5'])
  .factory('blacUtil', function(md5){
    var UUID = function(){};
    {
      UUID.prototype.createUUID = function(){
          var dg = new Date(1582, 10, 15, 0, 0, 0, 0);
          var dc = new Date();
          var t = dc.getTime() - dg.getTime();
          var tl = UUID.prototype.getIntegerBits(t,0,31);
          var tm = UUID.prototype.getIntegerBits(t,32,47);
          var thv = UUID.prototype.getIntegerBits(t,48,59) + '1'; // version 1, security version is 2
          var csar = UUID.prototype.getIntegerBits(UUID.prototype.rand(4095),0,7);
          var csl = UUID.prototype.getIntegerBits(UUID.prototype.rand(4095),0,7);
          var n = UUID.prototype.getIntegerBits(UUID.prototype.rand(8191),0,7) +
            UUID.prototype.getIntegerBits(UUID.prototype.rand(8191),8,15) +
            UUID.prototype.getIntegerBits(UUID.prototype.rand(8191),8,15) +
            UUID.prototype.getIntegerBits(UUID.prototype.rand(8191),0,15); // this last number is two octets long
          //return tl + '-' + tm  + '-' + thv  + '-' + csar + '-' + csl + n;
          return tl + tm  + thv  + csar + csl + n;  // 32位。去掉-
        };

      UUID.prototype.getIntegerBits = function(val,start,end){
        var base16 = UUID.prototype.returnBase(val,16);
        var quadArray = new Array();
        var quadString = '';
        var i = 0;
        for(i=0;i<base16.length;i++){
          quadArray.push(base16.substring(i,i+1));
        }
        for(i=Math.floor(start/4);i<=Math.floor(end/4);i++){
          if(!quadArray[i] || quadArray[i] == '') quadString += '0';
          else quadString += quadArray[i];
        }
        return quadString;
      };
      UUID.prototype.returnBase = function(number, base){
        return (number).toString(base).toUpperCase();
      };
      UUID.prototype.rand = function(max){
        return Math.floor(Math.random() * (max + 1));
      };
      var strDateTime = function(aTime, aOnlyDate){
        // 向后一天，用 new Date( new Date() - 0 + 1*86400000)
        // 向后一小时，用 new Date( new Date() - 0 + 1*3600000)
        if (!aTime) aTime = new Date();
        var l_date = new Array(aTime.getFullYear(),aTime.getMonth()<9?'0'+(aTime.getMonth()+1):(aTime.getMonth()+1),aTime.getDate()<10?'0'+aTime.getDate():aTime.getDate());
        if (aOnlyDate)
          return( l_date.join('-')) ; // '2014-01-02'
        else {
          var l_time = new Array(aTime.getHours() < 10 ? '0' + aTime.getHours() : aTime.getHours(), aTime.getMinutes() < 10 ? '0' + aTime.getMinutes() : aTime.getMinutes(), aTime.getSeconds() < 10 ? '0' + aTime.getSeconds() : aTime.getSeconds());
          return( l_date.join('-') + ' ' + l_time.join(':')); // '2014-01-02 09:33:33'
        }
      };
    }
    return {
      createUUID : UUID.prototype.createUUID,
      strDateTime : strDateTime,    // 向后一天，用 new Date( new Date() - 0 + 1*86400000)  1小时3600000
      strDate : function(arg1){ return strDateTime(arg1,true) },
      verifyBool : function (aParam){ return (aParam==true||aParam=="true"||aParam=="True")?true:false;  } ,
      md5String: md5.createHash,
      shareCache: { global:{} },
      wrapConfirm : function(aMsg,aObj){if(window.confirm(aMsg))aObj.apply(null, Array.prototype.slice.call(arguments,2) );}
      // 如果确认，就调用函数：aObj。并把后面的参数传递进去。
    }
  }) // md5加密支持
  .factory('blacStore', function(){
    var _debug = true;
    if(window.localStorage) console.log("check success -- > localStorage support!");
    else window.alert('This browser does NOT support localStorage. pls choose allow localstorage');
    var l_store = window.localStorage;
    var _storeUser = 'blacStoreLocalAdminUser',
        _storeWord = 'blacStoreLocalAdminWord',
        _storeRememberMe = 'blacStoreLocalAdminRem',
        _storeErr = 'blacStoreLocalErr';
    var verifyBool = function (aParam){ return (aParam==true||aParam=="true"||aParam=="True")?true:false;  };
    // typeof 返回的是字符串，有六种可能："number"、"string"、"boolean"、"object"、"function"、"undefined"

    return{
      // 设置和读取当前用户，名称，密码和保存密码。
      localRem: function(aArg){ if (aArg===undefined) return(verifyBool(l_store.getItem(_storeRememberMe)||"false")); else return(l_store.setItem(_storeRememberMe, aArg)); },
      localUser : function(aArg){ if (aArg===undefined) return(l_store.getItem(_storeUser)||""); else return(l_store.setItem(_storeUser, aArg));      },
      localWord: function(aArg){ if (aArg===undefined) return(l_store.getItem(_storeWord)||""); else return(l_store.setItem(_storeWord, aArg));    },
      getErr: function(){ return(l_store.getItem(_storeErr)); },
      setErr: function(){ if (_debug) console.log(arguments);
        if (arguments.length > 0) l_store.setItem(_storeErr, JSON.stringify(arguments)); else l_store.setItem('blacStoreLocalErr', '');
      },
      appendErr: function(){ if (_debug) console.log(arguments);
        if (arguments.length > 0) l_store.setItem(_storeErr, l_store.getItem(_storeErr) + JSON.stringify(arguments));
      },
      customGet:function(aKey){ return( JSON.parse( l_store.getItem(aKey)||'{}' ) ); },
      customSet:function(aKey, aObj) { return(l_store.setItem(aKey, JSON.stringify(aObj))) ;  },
      setLog:function(aObj){return(l_store.setItem('blacStoreStateLog', JSON.stringify(aObj))) ;}
    };
  })   // 本地存储支持
  .factory('blacPage', function(){
    function psGetContent(aFunGetList,aArgs,aOffset,aCallBack){
      /* psGetContent(blacAccess.getArticleList,[lLocation, lColumnId, .. ] ,
      /  通用查询函数：  服务对象的取内容函数，      内容函数的参数：第一个必须是定位对象。
      /  aoffset, function(aErr,aRtn){lp.contentList=aRtn.content;lp.psContentInfo=aRtn.psInfo })
      /  偏移量     返回函数。 aRtn里面有2个对象，一个是定位对象，一个是内容列表。
      */
      var psInfo = aArgs[0] // 得到定位参数。{ pageCurrent: 1, pageRows: 10, pageTotal: 0  };
      var lNoNeed = false; // 是否有必要查询。
      switch (aOffset) {
        case -1:
          if (psInfo.pageCurrent > 1) psInfo.pageCurrent = 1; else lNoNeed = true;
          break;
        case -2:
          if (psInfo.pageCurrent > 1) psInfo.pageCurrent -= 1; else lNoNeed = true;
          break;
        case -3:
          if (psInfo.pageCurrent < psInfo.pageTotal) psInfo.pageCurrent += 1; else lNoNeed = true;
          break;
        case -4:
          if (psInfo.pageCurrent < psInfo.pageTotal) psInfo.pageCurrent = psInfo.pageTotal; else lNoNeed = true;
          break;
        default :
          psInfo.pageCurrent = aOffset;
          break;
      }

      if (!lNoNeed) {
        aFunGetList.apply(null, aArgs).then(
          function (data){
            if (data.rtnCode == 1) {
              if (data.exObj.rowCount>0) psInfo.pageTotal = Math.floor(data.exObj.rowCount / psInfo.pageRows ) + 1;
              aCallBack(null, { content:data.exObj.contentList,
                                 psInfo: psInfo });
            }
            else aCallBack(data.rtnInfo, null);
          }
        );
      }
    };
    return {
      psGetContent:psGetContent
    }
  })
  .factory('blacAccess', function($location,$http,$q,md5,$rootScope){
    var lpUrl = '/rest/';
    var gEvent = { login:'event:login', broadcast:'event:broadcast' }
    var httpQ = function(aUrl, aObject){
      var deferred = $q.defer();
      /* $http.post(aUrl, aObject )
        .success(function (data, status, headers, config) {
          deferred.resolve(data || []);
        })
        .error(function (data, status, headers, config) {
          deferred.reject(status);
        });
      */
      $rootScope.$broadcast(gEvent.broadcast, "访问服务器...");
      $.ajax({
        async: false,
        crossDomain: false, // obviates need for sameOrigin test
        type: 'POST',
        dataType: 'json',
        url: aUrl,
        data: {jpargs: JSON.stringify(aObject)},
        success: function (returnData, returnMsg, ajaxObj, msgShow) {
          deferred.resolve(returnData || []);
          var lrtn = "ok";
          if (returnData.hasOwnProperty('rtnInfo')) lrtn = returnData.rtnInfo;
            $rootScope.$broadcast(gEvent.broadcast, "访问服务器..." + lrtn);
        },
          error: function (xhr, msg, e) {
            deferred.reject(msg);
            $rootScope.$broadcast(gEvent.broadcast, "访问服务器错误：" + msg);
        }
      });

      return deferred.promise;
    };
    var userLoginQ = function(aObjUser) {
      var lObjUser = angular.copy(aObjUser);
      lObjUser.md5 = md5.createHash(lObjUser.name + lObjUser.word);
      delete(lObjUser.word);
      delete(lObjUser.rem);
      return httpQ(lpUrl, { func: 'userlogin', ex_parm:{ user: lObjUser } } ); // user: {name:xx,word:xx}
    };
    var checkRtn = function (aRtn) {
      if (aRtn.rtnCode == 0)       // 当返回0的时候表示有后续的附加操作。进一步判断appendOper
        switch (aRtn.appendOper) {  // appendOper: login
          case 'login':
            $location.path('/');
            return false;
            break;
        };
      return true;
    };
    var dataState = { new: "new", dirty: 'dirty', clean: "clean" };

    return {   // xxx().then(function(data){}, function(err){})
      userLoginQ: userLoginQ,
      userChange:function(aUser,aOld,aNew){return httpQ( lpUrl,{func:'userChange',
        ex_parm:{user:aUser,old:md5.createHash(aUser+aOld), new: md5.createHash(aUser+aNew)}})},
      getAdminColumn:function(){return httpQ(lpUrl,{func:'getAdminColumn',ex_parm:{} })},
      setAdminColumn:function(aArgs){return httpQ(lpUrl,{func:'setAdminColumn',ex_parm:{columnTree: aArgs } })},
      getArticleList:function(aLoc,aColId){return httpQ(lpUrl,{func:'getArticleList',ex_parm:{columnId:aColId,location:aLoc} })},
      getArticleCont:function(aArtId){return httpQ(lpUrl,{func:'getArticleCont',ex_parm:{articleId:aArtId} })},
      setArticleCont:function(aArtObj){return httpQ(lpUrl,{func:'setArticleCont',ex_parm:{article:aArtObj} })},
      deleteArticleCont:function(aArtId){return httpQ(lpUrl,{func:'deleteArticleCont',ex_parm:{articleId:aArtId} })},


      getUserList:function(aLoc){return httpQ(lpUrl,{func:'getUserList',ex_parm:{ location:aLoc } })},
      setUserCont:function(aUser){return httpQ(lpUrl,{func:'setUserCont',ex_parm:{ user:aUser} })},

      deleteUserCont:function(aName){return httpQ(lpUrl,{func:'deleteUserCont',ex_parm:{name :aName }} ) },


      checkRtn: checkRtn,
      dataState : dataState,
      setDataState:function(aObj,aState){if($.isArray(aObj)) for(var i=0;i<aObj.length;i++)aObj[i]._exState=aState; else if(aObj) aObj._exState=aState;},
      getDataState:function(aObj) {return aObj._exState },
      gEvent:gEvent
    } ;

  })

;


$(document).ajaxStart(function(){ $("#loading").show(); });
$(document).ajaxStop(function(){ $("#loading").hide(); });