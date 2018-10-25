from . import web
from flask import request,jsonify,render_template
from models import db,Program_messages,User_messages,Gift,Awards,Share,ClickNubmer,ChannelTongji,Sharecontent
from urllib import request as req
import json
from datetime import datetime

# 获取微信小程序总表信息
@web.route('/program',methods=["POST","GET"])
def proMessage():
    if request.method == "GET":

        results_list = []
        results_dict = {}

        share_list = []
        channel_list = []
        program_res = db.session.query(Program_messages).all()
        sharecontent_res = db.session.query(Sharecontent).all()
        channeltongji_res = db.session.query(ChannelTongji).all()

        for p in program_res:

            if p:
                # 定义一个字典来接收数据库查询的数据
                p_dict = p.to_json()
                # 删除字典中不需要给客户端显示的字段
                del p_dict['id']
                del p_dict['click_numbers']
                results_list.append(p_dict)

                results_dict['proMessage'] = results_list
            else:
                results_dict['proMessage'] = {}

        for s in sharecontent_res:
            if s:

                s_dict = s.to_json()
                del s_dict['id']
                share_list.append(s_dict)

                results_dict['sharecontent'] = share_list
            else:
                results_dict['sharecontent'] = {}

        for c in channeltongji_res:
            if c :

                c_dict = c.to_json()
                del c_dict['id']
                channel_list.append(c_dict)
                results_dict['channelTongji'] = channel_list
            else:
                results_dict['channelTongji'] = {}

        return jsonify(results_dict)

    else:
        return '仅支持GET请求'

@web.route('/gettoken',methods=["POST","GET"])
def take_openid():
    if request.method == "GET":
        results_dict = {}

        get_appid = request.args.get('appid')
        get_appsecret = request.args.get('secret')
        get_token = request.args.get('token')

        # resp = req.urlopen("https://api.weixin.qq.com/sns/jscode2session?appid={}"
        #                    "&secret={}&token={}&grant_type=authorization_code".format
        #                    (get_appid,get_appsecret,get_token))

        resp = req.urlopen("https://api.weixin.qq.com/sns/jscode2session?appid={}"
                           "&secret={}&js_code={}&grant_type=authorization_code".format
                           (get_appid, get_appsecret, get_token))

        resp1 = resp.read().decode()
        resp2 = json.loads(resp1)

        keys_list = []
        for k in resp2.keys():
            keys_list.append(k)

        if 'openid'  in keys_list:
            openId = resp2['openid']
            res_users = db.session.query(User_messages).filter_by(openId=openId).first()

            if res_users is None:
                creat_user = User_messages(openId=openId)
                db.session.add(creat_user)
                db.session.commit()
                results_dict['openid'] = openId

            else:
                results_dict['openid'] = openId
                results_dict['gold_numbers'] = res_users.gold_numbers
                results_dict['awards'] = res_users.awards

            return jsonify(results_dict)

        else:
            return '获取ACCESS_TOKEN失败'

    else:
        return None

@web.route('/mall',methods=["GET","POST"])
def mall():
    if request.method == "GET":
        results_list = []
        results_dict ={}

        awards_res = db.session.query(Awards).all()

        for award_res in awards_res:
            award_res_dict = award_res.to_json()
            del award_res_dict['id']
            del award_res_dict['award_time']

            results_list.append(award_res_dict)
            results_dict['awards']=results_list

        return jsonify(results_dict)
    else:
        return None

# 分享游戏信息和精品礼包
@web.route('/gamemsg',methods=['GET','POST'])
def shareGame():
    if request.method == "GET":

        # 建立两个列表分别储存分享游戏信息，和精品礼包信息
        results_list1 = []
        results_list2 = []
        results_dict = {}

        # 取出两个数据库中的所有值返回
        res_games = db.session.query(Share).all()
        res_gifts = db.session.query(Gift).all()

        # for res_game,res_gift in zip(res_games,res_gifts):
        for res_game in res_games:

            res_game_dict = res_game.to_json()
            del res_game_dict['id']

            results_list1.append(res_game_dict)
            results_dict['shareGame'] = results_list1

        for res_gift in res_gifts:

            res_gift_dict = res_gift.to_json()
            del res_gift_dict['id']

            results_list2.append(res_gift_dict)
            results_dict['gift'] = results_list2


        return jsonify(results_dict)
    else:
        return None


# 获取小程序信息并且统计点击数
@web.route('/getProgram',methods=["GET","POST"])
def clickNumbers():
    if request.method == "GET":
        # results_dict = {}
        title_if = []
        get_appid = request.args.get('appid')

        res_gram = db.session.query(Program_messages).filter_by(appid=get_appid).first()
        # 去除appid 对应的点击数，进行请求＋１操作
        res_gram.click_numbers += 1

        # 取出appid　对应的数据，如果数据为空则说明该程序不在点击统计范围内则将其对应的数据加载到数据表，如果不为空，则更新点击数
        res_clicks = db.session.query(ClickNubmer).filter_by(appid=get_appid).first()

        if res_clicks is None:
            clicks = ClickNubmer(appid=res_gram.appid,title=res_gram.title, ClickNumbers=res_gram.click_numbers)
            db.session.add(clicks)
            db.session.commit()

        else:
            res_clicks.ClickNumbers = res_gram.click_numbers
            db.session.commit()

        return 'ok'
    else:
        return None

@web.route('/click',methods=['GET','POST'])
def click():
    if request.method == "GET":

        res_datas = db.session.query(ClickNubmer).all()
        return render_template('clicks.html',ClickDict = res_datas)

    else:
        return '错误的请求方法'


# 计算金币信息
@web.route('/gold',methods=["GET","POST"])
def operationGold():
    results_dict = {}
    if request.method == "GET":

        addgold = request.args.get('addGold',type=int)
        get_openId = request.args.get('openId')
        minusgold = request.args.get('minusGold',type=int)

        res_gold1 = db.session.query(User_messages).filter_by(openId=get_openId).first()

        if addgold and res_gold1 :
            res_gold1.gold_numbers = res_gold1.gold_numbers + addgold
            db.session.commit()

            results_dict['openid'] = res_gold1.openId
            results_dict['goldNumbers'] = res_gold1.gold_numbers

            return jsonify(results_dict)

        elif  minusgold and res_gold1:
            res_gold1.gold_numbers = res_gold1.gold_numbers - minusgold
            db.session.commit()

            results_dict['openid'] = res_gold1.openId
            results_dict['goldNumbers'] = res_gold1.gold_numbers

            return jsonify(results_dict)

        else:
            return 'openId输入错误,或者不支持的输入'

    else:
        return "不支持POST请求"

@web.route('/keepAwards',methods=["GET","POST"])
def getAwards():
    if request.method == "GET":
        get_id = request.args.get('awardid')
        get_openid = request.args.get('openid')
        # 获取奖品id为get_id的奖品信息
        get_award = db.session.query(Awards).filter_by(award_id=get_id).first()
        # 获取openId 为get_openid的用户信息
        get_user = db.session.query(User_messages).filter_by(openId=get_openid).first()
        # 数据库已经建立奖品和用户多对多的关系，此处是将用户和奖品进行关系绑定
        get_user.awards.append(get_award)
        # 更改获奖时间，为当前时间，及用户和奖品绑定时间
        get_award.award_time = datetime.now()
        db.session.commit()
        return 'ok'
    else:
        return None
web.route('/',methods=["GET","POST"])


# def test():
#     if request.method == "GET":
#         test_dic = {}
#         appid = request.args.get('appid')
#         appsecret = request.args.get('appsecret')
#         token =request.args.get('token')
#         res = db.session.query(User_messages).order_by(openId=appid).first()
#         if appid == 'a' and appsecret == 'b' and token == 'c':
#             test_dic['openid'] = res.openId
#             return jsonify(test_dic)
#         else:
#             return '获取失败'
#     return '不支持此操作'