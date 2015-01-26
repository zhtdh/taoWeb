#coding:utf-8
from django.db import connection,transaction
from django.shortcuts import render,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
from App.utils import log,AppException
from App.models import *
from App.ueditor.views import get_ueditor_controller
def test1(request):
    return render(request, "App/test.html")
def logon(session,p_user,p_rtn):
    ''' in structure
    { func: 'userlogin', ex_parm:{ user: { md5: "6547436690a26a399603a7096e876a2d"
                                           name: "aaa" }
                                 }
    }
    ls_err = ''
    '''
    ls_name = p_user['name']
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
            root = ArticleType(id='0',title='根',parent=None)
            root.save()
    else:
        if p_AType['state'] == 'new':
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
    if 'pageCurrent' not in p_dict['location'] or 'pageRows' not in p_dict['location'] or 'pageTotal' not in p_dict['location']:
        raise AppException('上传参数错误')
    firstRow = (p_dict['location']['pageCurrent'] - 1) * p_dict['location']['pageRows']
    lastRow = firstRow + p_dict['location']['pageRows']
    articles = list(Article.objects.filter(parent_id=p_dict['columnId'])\
                   .order_by('-rectime').values('id','title','recname','rectime')[firstRow:lastRow])
    if p_dict['location']['pageTotal'] == 0:
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
def setArticle(p_dict,p_rtn):
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
        new_article = Article(**p_article)
        new_article.save()
    elif state == 'dirty':
        id = p_article['id']
        del p_article['id']
        Article.objects.filter(id=id).update(**p_article)
    elif state == 'clean':
        pass
    else:
        raise AppException('上传参数错误')
    p_rtn.update({
        "rtnInfo": "成功",
        "rtnCode": 1,
    })
def deleteArticle(p_dict,p_rtn):
    if 'articleId' not in p_dict:
        raise AppException('上传参数错误')
    Article.objects.filter(id=p_dict['articleId']).delete()
    p_rtn.update({
        "rtnInfo": "成功",
        "rtnCode": 1,
    })


def dealREST_1(request):
    l_rtn = {
            "alertType": 0,
            "error":[],
            "rtnInfo": "",
            "rtnCode": -1,
            "exObj":{}
        }
    try:
        lPost = json.loads(list(request.POST.keys())[0]);
        log(lPost);

        #POST:{'{"func":"userlogin","ex_parm":{"user":{"name":"啊啊啊","md5":"897503af4d680930e913c669eaf0d1b2"}}}': ''},
        lFunc = lPost['func']
        lParm = lPost['ex_parm']
        if lFunc == 'userlogin':
            log(lParm);
            l_rtn["rtnCode"] = 1;
            return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))
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
def dealREST(request):
    l_rtn = {
            "alertType": 0,
            "error":[],
            "rtnInfo": "",
            "rtnCode": -1,
            "exObj":{}
        }

    try:
        ldict = json.loads(list(request.POST.keys())[0]);
        log(ldict);
        #ldict = json.loads(request.POST['jpargs'])
        #log(ldict)
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
                    setArticle(ldict['ex_parm'],l_rtn)
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