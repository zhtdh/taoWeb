//**************全局对象管理******************
// 声明一个全局对象Namespace，用来注册命名空间
Namespace = new Object();

// 全局对象仅仅存在register函数，参数为名称空间全路径，如"Grandsoft.GEA"
Namespace.register = function (fullNS) {
    // 将命名空间切成N部分, 比如Grandsoft、GEA等
    var nsArray = fullNS.split('.');

    var sEval = "";
    var sNS = "";
    for (var i = 0; i < nsArray.length; i++) {
        if (i != 0) sNS += ".";
        sNS += nsArray[i];
        // 依次创建构造命名空间对象（假如不存在的话）的语句
        // 比如先创建Grandsoft，然后创建Grandsoft.GEA，依次下去
        sEval += "if (typeof(" + sNS + ") == 'undefined') " + sNS + " = new Object();"
    }
    if (sEval != "") eval(sEval);
}
//**************全局对象管理******************
//注册sy对象 自定义工具 空间
Namespace.register('sy');

sy.getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

sy.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
sy.csrftoken = sy.getCookie('csrftoken');
//***************设置Ajax默认参数********************

$.ajaxSetup({
    async: false,
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!sy.csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", sy.csrftoken);
        }
    },
    type: 'POST',
    //contentType: 'application/x-www-form-urlencoded;charset=utf-8',

    dataType: 'json',
    success: function (returnData, returnMsg, ajaxObj, msgShow) {
        var stateCod = parseInt(returnData.stateCod);
        if (returnData && !isNaN(stateCod)) {
            if (stateCod > 0) {//返回成功
                if (msgShow == false) {
                    return true;
                }
                if (stateCod >= 101 && stateCod <= 200) {
                    $.messager.alert('提示', returnData.msg || '执行成功！', 'info');
                }
                if (stateCod >= 201 && stateCod <= 300) {
                    $.messager.show({
                        title: '',
                        msg: returnData.msg || '执行成功!',
                        timeout: 3000,
                        showType: 'slide'
                    });
                }
                return true;
            } else {//返回错误
                if (returnData.msg && returnData.msg.length > 0) {
                    $.messager.alert('提示', returnData.msg, 'info');
                }
                if (returnData.error && returnData.error.length > 0) {
                    $.messager.show({
                        title: '错误信息',
                        msg: returnData.error.join('\n'),
                        timeout: 3000,
                        showType: 'slide'
                    });
                }
                if (stateCod <= -101 && stateCod >= -200) {//系统级错误返回登录界面
                    sy.onError(returnData.msg, true);
                }
                return false;
            }
        } else {
            $.messager.alert('错误', '返回数据错误！', 'error');
            return false;
        }
    },
    error: function (xhr, msg, e) {
        console.info('服务器错误');
        //sy.onError('服务器错误：' + msg, false);
    }

});
