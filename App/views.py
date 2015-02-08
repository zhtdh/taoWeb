#coding:utf-8
from django.db import connection,transaction
from django.shortcuts import render,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError,DatabaseError
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from App.utils import log,AppException,logErr
from App.models import *
from App.ueditor.views import get_ueditor_controller

def test1(request):
    return render(request, "App/test.html")
def paramCheck(standard_set,target_set,check_type):
    '''
    检查参数是否合法
    :param standard_set:标准set
    :param target_set: 检验set
    :param check_type: (‘必要’,'')
    :return:
    '''
def getPageRowNo(p_dict):
    '''
    返回分页firstRow,lastRow
    :param p_dict: {pageCurrent:当前页, pageRows:一页的行数,pageTotal: 0}
    :return: (firstRowNo,lastRowNo)
    '''
    if 'pageCurrent' not in p_dict or 'pageRows' not in p_dict or 'pageTotal' not in p_dict:
        raise AppException('上传分页参数错误')
    if not (isinstance(p_dict['pageCurrent'],int) and \
                    isinstance(p_dict['pageRows'],int) and \
                    isinstance(p_dict['pageTotal'],int)):
        raise AppException('上传分页参数错误')
    firstRow = (p_dict['pageCurrent'] - 1) * p_dict['pageRows']
    lastRow = firstRow + p_dict['pageRows']
    if p_dict['pageTotal'] == 0:
        rowTotal = 0
    else:
        rowTotal = -1;
    return (firstRow,lastRow,rowTotal)
def logon(session,p_user,p_rtn):
    '''

    :param session:
    :param p_user: { md5: "6547436690a26a399603a7096e876a2d"
                                           username: "aaa" }
    :param p_rtn:
    :return:
    '''
    ls_name = p_user['username']
    ls_pw = p_user['md5']
    try:
        user = User.objects.get(username=ls_name)
        if user.pw == ls_pw:
            session['username'] = ls_name
            p_rtn.update({
                "rtnInfo":"登录成功",
                "rtnCode":1
            })
        else:
            session["username"] = None
            p_rtn.update({
                "rtnInfo":"密码错误",
                "rtnCode":-1
            })
    except ObjectDoesNotExist:
        p_rtn.update({
            "rtnInfo":"用户不存在",
            "rtnCode":-1
        })

def saveArticleType(p_AType):
    if str(p_AType['id']) == '0':
        if not ArticleType.objects.filter(id='0').exists():
            root = ArticleType(id='0',title='根',parent_id=None)
            root.save()
    else:
        if 'state' not in p_AType:
            pass
        elif p_AType['state'] == 'new':
            if 'id' not in p_AType:
                raise AppException('新文章类型id非法')
            if 'parentId' not in p_AType:
                raise AppException('新文章类型parentId非法')
            if 'title' not in p_AType:
                raise AppException('新文章类型title非法')
            newType = ArticleType(id=p_AType['id'],parent_id=str(p_AType['parentId']),title=p_AType['title'])
            if 'ex_parm' in p_AType:
                if 'kind' in p_AType['ex_parm']:
                    newType.kind = p_AType['ex_parm']['kind']
                if 'link' in p_AType['ex_parm']:
                    newType.link = p_AType['ex_parm']['link']
            newType.save()
        elif p_AType['state'] == 'dirty':
            if 'id' not in p_AType:
                raise AppException('文章类型id非法')
            oldType = ArticleType.objects.get(id=p_AType['id'])
            if (('parentId' in p_AType) and (oldType.parent_id != str(p_AType['parentId']))):
                oldType.parent_id = str(p_AType['parentId'])
            if (('title' in p_AType) and (oldType.title != p_AType['title'])):
                oldType.title = p_AType['title']
            if 'ex_parm' in p_AType:
                if 'kind' in p_AType['ex_parm']:
                    if oldType.kind != p_AType['ex_parm']['kind']:
                        oldType.kind = p_AType['ex_parm']['kind']
                if 'link' in p_AType['ex_parm']:
                    if oldType.link != p_AType['ex_parm']['link']:
                        oldType.link = p_AType['ex_parm']['link']
            oldType.save()
        elif p_AType['state'] == 'clean':
            pass
        else:
            raise AppException('类型修改state非法!')
    if 'items' in p_AType:
        for item in p_AType['items']:
            saveArticleType(item)
def dealArticleType(p_dict,p_rtn):
    '''
    :param p_dict = {
        "id": 0,
        "title": "根",
        "items": [
          {
            "id": "C67743685CF00001FFEB15602B167D",
            "parentId": 0,
            "title": "新节点1",
            "state": "clean",
            "ex_parm": { kind:"", link:""},
            "items": []
          }],
        "deleteId": [xxx, xxx]
      }
      state说明：
              new：生成insert，
              dirty：生成update语句。
              clean：不用
    :param p_rtn: 返回结构
    :return:
    '''

    if 'deleteId' in p_dict:
        ArticleType.objects.filter(id__in=p_dict['deleteId']).delete()
    if 'id' in p_dict:
        saveArticleType(p_dict)
    p_rtn.update({
        "alertType": 1,
        "error":[],
        "rtnInfo": "成功",
        "rtnCode": 1
    })
def getArticleType(p_rtn):
    '''
    返回全部ArticleType
    :param p_rtn:
    :return:
    '''
    l_rtn = {}
    try:
        root = ArticleType.objects.get(id='0')
        l_rtn.update({
            'id' : '0',
            'parentId':None,
            'title':'根',
            'items':[]
        })
        getSubArticleType('0',l_rtn['items'])
        p_rtn.update({
            "rtnInfo":"查询成功",
            "rtnCode":1,
            "exObj":{
                "columnTree" : l_rtn
            }
        })
    except ObjectDoesNotExist:
        p_rtn.update({
            "rtnInfo":"根不存在",
            "rtnCode":-1
        })
def getSubArticleType(p_parentId,p_items):
    a_type = ArticleType.objects.filter(parent_id=p_parentId)
    for t in a_type:
        items = []
        getSubArticleType(t.id,items)
        p_items.append({
            'id' : t.id,
            'parentId' : t.parent_id,
            'title':t.title,
            'ex_parm':{
                'link':t.link,
                'kind':t.kind
            },
            'items':items
        })
def getArticleList(p_dict,p_rtn):
    '''
    :param p_dict:{
        location: { pageCurrent:当前页, pageRows:一页的行数,pageTotal:共有多少页 },
        columnId:'xxx'
     }
    :return:
    '''
    if 'columnId' not in p_dict or 'location' not in p_dict:
        raise AppException('上传参数错误')
    firstRow,lastRow,rowTotal = getPageRowNo(p_dict['location'])
    articles = list(Article.objects.filter(parent_id=p_dict['columnId'])\
                   .order_by('-rectime').values('id','title','recname','rectime')[firstRow:lastRow])
    if rowTotal == 0:
        total = Article.objects.filter(parent_id=p_dict['columnId']).count()
    else:
        total = -1
    p_rtn.update({
        "alertType": 1,
        "error":[],
        "rtnInfo": "成功",
        "rtnCode": 1,
        "exObj":{
            "rowCount" : total,
            "contentList" : articles
        }
    })
def getArticle(p_dict,p_rtn):
    '''
    查询指定article
    :param p_dict: { articleId: xxx }
    :param p_rtn:
    :return:
    '''
    if 'articleId' not in p_dict:
        raise AppException('上传参数错误')
    try:
        article = Article.objects.get(id=p_dict['articleId'])
        p_rtn.update({
            "rtnInfo":"成功",
            "rtnCode":1,
            "exObj" : {
                "article" : {
                    "id" : article.id,
                    "parentid" : article.parent_id,
                    "kind" : article.kind,
                    "title":article.title,
                    "content":article.content,
                    "imglink":article.imglink,
                    "videolink":article.videolink,
                    "recname":article.recname,
                    "rectime":article.rectime
                }
            }
        })
    except ObjectDoesNotExist:
        p_rtn.update({
            "rtnInfo":"失败",
            "rtnCode":-1
        })
def setArticle(p_dict,p_rtn,session):
    '''
    增删改Article
    :param p_dict:{ article:{
                        state:"new",
                        id: 'xxxxx',
                        parentid:0,
                        kind:"",
                        title:"",
                        content:"",
                        imglink:"",
                        videolink:"",
                        recname:"",
                        rectime:""
                    }
                 }
        state说明：
              new：生成insert，
              dirty：生成update语句。
              clean：不用
    :param p_rtn:
    :return:
    '''
    if "article" not in p_dict:
        raise AppException('上传参数错误')
    p_article = p_dict['article'].copy()
    if 'state' not in p_article:
        raise AppException('上传参数错误')
    p_article.update({
        'parent_id':p_article['parentid']
    })
    del p_article['parentid']
    state = p_article['state']
    del p_article['state']
    if state == 'new':
        p_article.update({
            "recname" : session["username"],
            "rectime" : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        new_article = Article(**p_article)
        new_article.save()
    elif state == 'dirty':
        if session['username'] == p_article['recname'] or session['username'] == 'Admin':
            id = p_article['id']
            del p_article['id']
            del p_article['recname']
            del p_article['rectime']
            Article.objects.filter(id=id).update(**p_article)
        else:
            p_rtn.update({
                "rtnInfo": "非本人发布，不能修改",
                "rtnCode": -1
            })
    elif state == 'clean':
        pass
    else:
        raise AppException('上传参数错误')
    p_rtn.update({
        "rtnInfo": "成功",
        "rtnCode": 1
    })
def deleteArticle(p_dict,p_rtn,session):
    if 'articleId' not in p_dict:
        raise AppException('上传参数错误')
    old_article = Article.objects.get(id=p_dict['articleId'])
    if session['username'] == old_article.recname or session['username'] == 'Admin':
        old_article.delete()
        p_rtn.update({
            "rtnInfo": "成功",
            "rtnCode": 1
        })
    else:
        p_rtn.update({
            "rtnInfo": "非本人发布，不能删除",
            "rtnCode": -1
        })
def setUser(p_dict,p_rtn,session):
    '''
    维护User
    :param p_dict: { state:"new", username: xxx , pw : xxx, oldWord: xxx}
    :param p_rtn:
    :return:
    '''
#    p_dict = p_dict['user']
    p_set = set(p_dict.keys())
    p_checkset = set(['_exState','username','pw'])
    if p_set != p_checkset:
        raise AppException('上传参数错误')
    if session['username'] == 'Admin':
        try:
            if p_dict['_exState'] == 'new':
                new_u = User(username=p_dict['username'],pw=p_dict['pw'])
                new_u.save(force_insert=True)
            elif p_dict['_exState'] == 'dirty':
                old_u = User.objects.get(username=p_dict['username'])
                if old_u.pw == p_dict['oldword']:
                    old_u.pw = p_dict['pw']
                    old_u.save(force_update=True,update_fields=['pw'])
                else:
                    p_rtn.update({
                        "rtnInfo": "失败，旧密码错误",
                        "rtnCode": -1
                    })
            elif p_dict['_exState'] == 'clean':
                pass
            else:
                raise AppException('上传参数错误')
            p_rtn.update({
                "rtnInfo": "成功",
                "rtnCode": 1
            })
        except IntegrityError:
            p_rtn.update({
                "rtnInfo": "用户名重复，增加失败！",
                "rtnCode": -1
            })
        except DatabaseError:
            p_rtn.update({
                "rtnInfo": "用户不存在，修改失败！",
                "rtnCode": -1
            })
    else:
        p_rtn.update({
            "rtnInfo": "非管理员不能维护用户",
            "rtnCode": -1
        })
def deleteUser(p_dict,p_rtn,session):
    '''
    删除user
    :param p_dict: { username: xxx }
    :param p_rtn:
    :param session:
    :return:
    '''
    if 'username' not in p_dict:
        raise AppException('上传参数错误')
    if session['username'] == 'Admin':
        User.objects.filter(username=p_dict['username']).delete()
        p_rtn.update({
            "rtnInfo": "成功",
            "rtnCode": 1
        })
    else:
        p_rtn.update({
            "rtnInfo": "非管理员不能删除用户",
            "rtnCode": -1
        })
def getUserList(p_dict,p_rtn):
    '''
    :param p_dict:{
        pageCurrent:当前页, pageRows:一页的行数,pageTotal:共有多少页
     }
    :return:
    '''

    firstRow,lastRow,rowTotal = getPageRowNo(p_dict)
    users = list(User.objects.exclude(username__exact='Admin').order_by('username').values('username')[firstRow:lastRow])
    if rowTotal == 0:
        total = User.objects.all().count()
    else:
        total = -1
    p_rtn.update({
        "alertType": 1,
        "error":[],
        "rtnInfo": "成功",
        "rtnCode": 1,
        "exObj":{
            "rowCount" : total,
            "userList" : users
        }
    })
def resetPw(p_dict,p_rtn):
    '''
    修改用户密码
    :param p_dict:{ "username":"Admin",
                    "old":"89dc2302d644609526f8bee192df43e3",
                    "new":"0977648895559d3a4420c397bc6cf98d"
                  }
    :param p_rtn:
    :return:
    '''
    try:
        user = User.objects.get(username=p_dict['username'])
        if user.pw != p_dict['old']:
            p_rtn.update({
            "rtnInfo":"密码错误",
            "rtnCode":-1
        })
        else:
            user.pw = p_dict['new']
            user.save(update_fields=['pw'])
            p_rtn.update({
                "rtnInfo":"成功",
                "rtnCode":1
            })
    except ObjectDoesNotExist:
        p_rtn.update({
            "rtnInfo":"用户名错误",
            "rtnCode":-1
        })
def getArticleTypesByKind(p_dict,p_rtn):
    '''
    模糊查询kind值，返回ArticleType数组
    :param p_dict: {kind:['',''],parentId:xxx}
    :param p_rtn:
    :return:
    '''
    p_set = set(p_dict.keys())
    p_checkset = set(['kind','parentId'])
    if p_set != p_checkset:
        raise AppException('上传参数错误')
    if not (isinstance(p_dict['parentId'],str) and isinstance(p_dict['kind'],list)):
        raise AppException('上传参数错误')
    if len(p_dict['parentId']) > 0:
        r = ArticleType.objects.filter(parent_id=p_dict['parentId'])
    else:
        r = ArticleType.objects.all()
    if len(p_dict['kind']) > 0:
        pattern = '('
        for p in p_dict['kind']:
            pattern = pattern + p + '|'
        #pattern = len(pattern) == 1 and '()' or pattern[0:-1] + ')'
        pattern = pattern[0:-1] + ')'
        r = r.filter(kind__regex=pattern)
    rtn_list = list(r.values('id','title','link','kind','parent_id'))
    p_rtn.update({
        "rtnInfo": '成功',
        "rtnCode": 1,
        "exObj":{
            "contentList" : rtn_list
        }
    })
def getArticlesByKind(p_dict,p_rtn):
    '''
    模糊查询kind值，返回Article数组
    :param p_dict: {kind:['',''],parentId:xxx,id:xxx,
                    location: { pageCurrent: 1, pageRows: 10, pageTotal: 0},
                    parentKind: ['xxx','xxx'],
                    hasContent: 1 返回记录中包括content，other：不包括。
                    }
    :param p_rtn:
    :return:
    '''
    p_set = set(p_dict.keys())
    p_checkset = set(['kind','parentId','id','location','parentKind'])
    if p_set != p_checkset:
        raise AppException('上传参数错误1')
    if not (isinstance(p_dict['parentId'],str) and\
                    isinstance(p_dict['id'],str) and\
                    isinstance(p_dict['kind'],list) and\
                    isinstance(p_dict['location'],dict)):
        raise AppException('上传参数错误2')
    firstRow,lastRow,rowTotal = getPageRowNo(p_dict['location'])
    if len(p_dict['id']) > 0:
        r = Article.objects.filter(id=p_dict['id'])
    else:
        if len(p_dict['parentId']) > 0: #parentId
            r = Article.objects.filter(parent_id=p_dict['parentId'])
        else:
            r = Article.objects.all()
        if len(p_dict['kind']) > 0:
            artKindReg = '('
            for p in p_dict['kind']:
                artKindReg = artKindReg + p + '|'
            #pattern = len(pattern) == 1 and '()' or pattern[0:-1] + ')'
            artKindReg = artKindReg[0:-1] + ')'
            r = r.filter(kind_regex=artKindReg)
        if len(p_dict['parentKind']) > 0:
            colKindReg = '('
            for p in p_dict['kind']:
                colKindReg = colKindReg + p + '|'
            colKindReg = colKindReg[0:-1] + ')'
            r = r.filter(parent__kind__regex=colKindReg)
    if rowTotal == 0:
        total = r.count()
    else:
        total = -1
    r = r.order_by('-rectime')
    if p_dict.get('hasContent',0) == 1:
        rtn_list = list(r.values('id','title','content','parent_id','kind','imglink','videolink')[firstRow:lastRow])
    else:
        rtn_list = list(r.values('id','title','parent_id','kind','imglink','videolink')[firstRow:lastRow])
    p_rtn.update({
        "rtnInfo": "成功",
        "rtnCode": 1,
        "exObj":{
            "rowCount" : total,
            "contentList" : rtn_list
        }
    })

def dealREST(request):
    l_rtn = {
            "alertType": 0,
            "error":[],
            "rtnInfo": "",
            "rtnCode": -1,
            "exObj":{}
        }

    try:
        log(request.POST);
        ldict = json.loads(request.POST['jpargs']);
        log(ldict);

        if 'ex_parm' not in ldict or 'func' not in ldict:
            raise AppException('传入参数错误')
        with transaction.atomic():
            if ldict['func'] == 'userlogin':
                logon(request.session,ldict['ex_parm']['user'],l_rtn)
            else:
                # if ('username' not in request.session or request.session['username'] == None):
                #     return HttpResponse(json.dumps({
                #         "rtnCode":0,
                #         "rtnInfo":"登录不成功",
                #         "alertType":0,
                #         "error":[],
                #         "exObj":{},
                #         "appendOper": "login"
                #     },ensure_ascii=False), content_type="application/javascript")
                if ldict['func'] == 'setAdminColumn':
                    dealArticleType(ldict['ex_parm']['columnTree'],l_rtn)
                elif ldict['func'] == 'getAdminColumn':
                    getArticleType(l_rtn)
                elif ldict['func'] == 'getArticleList':
                    getArticleList(ldict['ex_parm'],l_rtn)
                elif ldict['func'] == 'getArticleCont':
                    getArticle(ldict['ex_parm'],l_rtn)
                elif ldict['func'] == 'setArticleCont':
                    setArticle(ldict['ex_parm'],l_rtn,request.session)
                elif ldict['func'] == 'deleteArticleCont':
                    deleteArticle(ldict['ex_parm'],l_rtn,request.session)
                elif ldict['func'] == 'setUserCont':
                    setUser(ldict['ex_parm']['user'],l_rtn,request.session)
                elif ldict['func'] == 'deleteUserCont':
                    deleteUser(ldict['ex_parm'],l_rtn,request.session)
                elif ldict['func'] == 'getUserList':
                    getUserList(ldict['ex_parm']['location'],l_rtn)
                elif ldict['func'] == 'userChange':
                    resetPw(ldict['ex_parm'],l_rtn)
                elif ldict['func'] == 'getForeCol':
                    getArticleTypesByKind(ldict['ex_parm'],l_rtn)
                elif ldict['func'] == 'getForeArt':
                    getArticlesByKind(ldict['ex_parm'],l_rtn)
                elif ldict['func'] == 'extools':
                    l_rtn = rawsql4rtn(ldict['ex_parm']['sql']);
                else:
                    l_rtn.update({
                        "rtnInfo":"功能错误",
                        "rtnCode":-1
                    })
    except AppException as e:
        l_rtn = {
            "alertType": 0,
            "error":[],
            "rtnInfo": str(e),
            "rtnCode": -1,
            "exObj":{}
        }
    except Exception as e:
        log("ajaxResp.dealPAjax执行错误：%s" % str(e.args))
        l_rtn = {
            "alertType": 0,
            "error":e.args,
            "rtnInfo": "服务器端错误",
            "rtnCode": -1,
            "exObj":{}
        }
    finally:
        for q in connection.queries:
            log(q)
    return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))
def ueditorController(request):
    if ('username' not in request.session or request.session['username'] == None):
        return HttpResponse(json.dumps({
            "rtnCode":0,
            "rtnInfo":"登录不成功",
            "alertType":0,
            "error":[],
            "exObj":{},
            "appendOper": "login"
        },ensure_ascii=False), content_type="application/javascript")
    return get_ueditor_controller(request)

def rawsql4rtn(aSql):
    '''
        根据sql语句，返回数据和记录总数。.
    '''
    l_cur = connection.cursor()
    l_rtn = {"error":"",
            "rtnInfo": "成功",
            "rtnCode": 1,
            "exObj":{} }
    l_sum = []
    try:
        log(aSql)
        l_cur.execute(aSql)
        for i in l_cur.fetchall():
            l_sum.append(i)
    except Exception as e:
        logErr("查询失败：%s" % str(e.args))
        raise e
    finally:
        l_cur.close()
    l_rtn.update( { "exObj": l_sum } )
    return l_rtn