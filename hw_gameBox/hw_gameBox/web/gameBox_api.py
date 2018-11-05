from . import web
from flask import request, jsonify, render_template, redirect, url_for, g
from models import db,Program_messages,User_messages,Gift,Awards,Share,ClickNubmer,\
                    ChannelTongji,Sharecontent,Award_record
from urllib import request as req
import json
from datetime import datetime
from fuction.WXBizDataCrypt import WXBizDataCrypt
from forms import ClickForm


# 获取微信小程序总表信息
@web.route('/program',methods=["POST","GET"])
def proMessage():
    if request.method == "GET":
        get_appid = request.args.get('appid')
        get_channel = request.args.get('channel')
        get_position = request.args.get('position')

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
            sessionKey = resp2['session_key']
            res_user = db.session.query(User_messages).filter_by(openId=openId).first()

            # 判断用户是否为新用户，如果是信息用户，则添加用户信息，并且将返回用户状态码
            if res_user is None:
                creat_user = User_messages(openId=openId)
                db.session.add(creat_user)
                db.session.commit()
                results_dict['openid'] = openId
                results_dict['sessionKey'] = sessionKey
                results_dict['isexist'] = 0

            else:
                results_dict['openid'] = openId
                results_dict['gold_numbers'] = res_user.gold_numbers
                results_dict['isexist'] = 1
                results_dict['sessionKey'] = sessionKey

                # 根据用户openid 查询用户所有奖品id　添加到aw_list中
                # 取用户获取奖品的最新10条
                res_award_records = db.session.query(Award_record).filter_by(user_id=openId).order_by(
                    Award_record.id.desc()).limit(10).all()
                aw_list = []

                for res_award_record in res_award_records:
                    aw_list.append(res_award_record.award_id)

                # 遍历奖品id列表，查询奖品，将所有奖品添加到一个列表中
                awards_list = []
                for k in aw_list:
                    if k:
                        res_aw = db.session.query(Awards).filter_by(awardId=k).first()
                        # 把奖品最新时间更新，而不是同一种奖品，之前的获奖时间
                        res_aw_re = db.session.query(Award_record).filter_by(award_id=k).order_by(
                            Award_record.id.desc()).first()
                        dict_a = {
                            'awardtitle':res_aw.awardTitle,
                            'awardtime':res_aw_re.award_time
                        }
                        awards_list.append(dict_a)
                        results_dict['awards'] = awards_list
                    else:
                        results_dict['awards'] = []
                return jsonify(results_dict)

        else:
            return '获取ACCESS_TOKEN失败'

    else:
        return '不支持的请求方法'

@web.route('/mall',methods=["GET","POST"])
def mall():
    if request.method == "GET":
        results_list = []
        results_dict = {}
        awards_res = db.session.query(Awards).all()

        for award_res in awards_res:
            awards_dict = {
                'awardId':award_res.awardId,
                'awardTitle':award_res.awardTitle
            }
            results_list.append(awards_dict)
            results_dict['awards'] = results_list
           
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
# @web.route('/getProgram',methods=["GET","POST"])
# def clickNumbers():
#     if request.method == "GET":
#         # results_dict = {}
#         title_if = []
#         get_appid = request.args.get('appid')
#
#         res_gram = db.session.query(Program_messages).filter_by(appid=get_appid).first()
#         # 去除appid 对应的点击数，进行请求＋１操作
#         res_gram.click_numbers += 1
#
#         # 取出appid　对应的数据，如果数据为空则说明该程序不在点击统计范围内则将其对应的数据加载到数据表，如果不为空，则更新点击数
#         res_clicks = db.session.query(ClickNubmer).filter_by(appid=get_appid).first()
#
#         if res_clicks is None:
#             clicks = ClickNubmer(appid=res_gram.appid,title=res_gram.title, ClickNumbers=res_gram.click_numbers)
#             db.session.add(clicks)
#             db.session.commit()
#
#         else:
#             res_clicks.ClickNumbers = res_gram.click_numbers
#             db.session.commit()
#
#         return 'ok'
#     else:
#         return None
#
# @web.route('/click',methods=['GET','POST'])
# def click():
#     if request.method == "GET":
#
#         res_datas = db.session.query(ClickNubmer).all()
#         return render_template('c.html',ClickDict = res_datas)
#
#     else:
#         return '错误的请求方法'


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
    results_list = []
    if request.method == "GET":
        get_id = request.args.get('awardid',type=int)
        get_openid = request.args.get('openid')

        # 将记录存入获奖记录表
        award_id_list = []
        # 查询奖品表中所有的奖品id 为了方便后面判断输入的奖品id是否在奖品库中
        awasId = db.session.query(Awards).all()
        for awaId in awasId:
            award_id_list.append(awaId.awardId)

        # 判断输入的奖品id是否在奖品表中，如果在就继续执行，如果不在则返回提示信息
        if get_id in award_id_list:

            time =datetime.now().strftime('%Y-%m-%d')
            new_record = Award_record(user_id=get_openid,award_id=get_id,award_time=time)
            db.session.add(new_record)
            db.session.commit()

            # 通过获奖记录表查询用户获奖记录
            # 先查询每个openid　对应多少个award_id记录
            user_awards = db.session.query(Award_record).filter_by(user_id=get_openid).order_by(
                Award_record.id.desc()).limit(10).all()

            # 取出获奖记录表中的所有award_id 添加到awards_list
            awards_list = []
            for user_award in user_awards:
                awards_list.append(user_award.award_id)

            # 通过奖品列表，遍历所有award_id值，通过这个值查询对应的奖品信息
            for aw_id in awards_list:
                # 因为奖品id是根据用户id　来获取，所以一个用户有多少奖品id，对应的就有多少个奖品标题，和获奖时间，first()就可以了
                a = db.session.query(Awards).filter_by(awardId=aw_id).first()
                b = db.session.query(Award_record).filter_by(award_id=aw_id).order_by(Award_record.id.desc()).first()

                # 构造字典存储奖品标题和获奖时间
                dict_a = {
                    "awardtitle":a.awardTitle,
                    "awardtime":b.award_time
                }
                results_list.append(dict_a)
            return jsonify(results_list)

        else:
            return "奖品库没有该awardid"

    else:
        return "不支持的访问方法"

@web.route('/getOpenGid',methods=["GET","POST"])
def getOpenGid():
    if request.method == "GET":
        appId = request.args.get('appId',default=str)
        sessionKey = request.args.get('sessionKey',default=str)
        encryptedData = request.args.get('encryptedData',default=str)
        iv = request.args.get('iv')

        pc = WXBizDataCrypt(appId, sessionKey)
        resPc = pc.decrypt(encryptedData, iv)

        return jsonify(resPc)

    elif request.method == "POST":
        appId = request.args.get('appId',default=str)
        sessionKey = request.args.get('sessionKey',default=str)
        encryptedData = request.args.get('encryptedData',default=str)
        iv = request.args.get('iv')
        print(appId)

        pc = WXBizDataCrypt(appId, sessionKey)
        resPc = pc.decrypt(encryptedData, iv)

        return jsonify(resPc)


@web.route('/saveClick',methods=["GET","POST"])
def click():
    if request.method == "GET":
        get_name = request.args.get('name')
        get_channel = request.args.get('channel')

        res_clicknumbers = db.session.query(ClickNubmer).filter_by(name=get_name).all()

        # 取出表中所有的channel值组成列表
        chanel_list = []
        for res_clicknumber in res_clicknumbers:
            chanel_list.append(res_clicknumber.channel)

        # 首先判断取到的值，是否在数据库列表中，如果没有的情况下，那么传入的数据就是新数据，那么就应该将这一组数据存入数据库
        if len(res_clicknumbers) == 0:
            # 找出数据库sortId的最大值，对该值+1赋值给新的数据
            res_sortId_max = db.session.query(ClickNubmer).order_by(ClickNubmer.sortId.desc()).first().sortId
            # 排序仅针对数据库特定的那几组数据排序，所以sortId 不用赋值
            save_click = ClickNubmer(sortId=res_sortId_max+1,name=get_name,channel=get_channel,clicks=1,cha_clicks=1)
            db.session.add(save_click)

            db.session.commit()

        # 如果res_clicknumber 不为None 说明数据库中存在name=get_name的值，那么需要将所有name值取出，对ClickNumber做加1操作
        # 同时这还分为两种情况，如果channel存在为一种情况，channel不存在又是一种情况，将这两种情况区分开的话，那么到时候统计点击数
        # 的时候可以将name和channel分开统计

        # 如果name存在并且channel存在
        elif get_channel in chanel_list:
            res_channel = db.session.query(ClickNubmer).filter_by(name=get_name,channel=get_channel).first()
            # 对这条记录的clickNumbers　进行加１操作
            res_channel.cha_clicks +=1
            db.session.commit()

            # 查询出数据库中所有name=?的值，取出clicks最大的值，然后进行加１,再然后将数据库中所有的name=?的clicks　都换成最大值
            res_max = db.session.query(ClickNubmer).order_by(ClickNubmer.clicks.desc())\
                .filter_by(name=get_name).first().clicks
            save_max = res_max + 1

            # 取出数据库中所有name 为get_name的数据，然后将该数据中的clicks进行赋值，赋值后的所有clicks将会同步
            res_clicks = db.session.query(ClickNubmer).filter_by(name=get_name).all()
            for res_click in res_clicks:
                res_click.clicks = save_max
            db.session.commit()


        # 如果name存在并且channel不存在，那么就要创造这条记录，clickNumbers赋值为１
        elif get_channel not in chanel_list:
            res_channel = db.session.query(ClickNubmer).filter_by(name=get_name).first()
            save_click = ClickNubmer(name=get_name,channel=get_channel,cha_clicks=1,sortId=res_channel.sortId)
            db.session.add(save_click)
            db.session.commit()
            res_max = db.session.query(ClickNubmer).order_by(ClickNubmer.clicks.desc()) \
                .filter_by(name=get_name).first().clicks
            save_max = res_max + 1
            res_clicks = db.session.query(ClickNubmer).filter_by(name=get_name).all()
            for res_click in res_clicks:
                res_click.clicks = save_max
            db.session.commit()


        return '保存成功'

    else:
        return '不支持的请求方法'


@web.route('/click',methods=["GET","POST"])
def getclick():

    form = ClickForm()
    if form.validate_on_submit():
        name = form.name.data
        channel = form.channel.data

        if name == 'all' and channel == 'all':
            res_all = db.session.query(ClickNubmer).all()

        # return redirect(url_for('web.findClick'))
            return render_template('allclicks.html',ClickDict = res_all)

        else:
            res_find = db.session.query(ClickNubmer).filter_by(name=name,channel=channel).all()
            return render_template('allclicks.html',ClickDict = res_find)
    # 为实现固定数量显示，首先对sortId进行升序排列，然后筛选前n条数据
    res_datas = db.session.query(ClickNubmer).order_by(ClickNubmer.sortId.asc()).filter(ClickNubmer.sortId<=10).all()
    return render_template('click.html',form=form,ClickDict = res_datas)





