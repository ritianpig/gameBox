from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db,Program_messages,User_messages,Awards,Gift,Share,ClickNubmer,Sharecontent,ChannelTongji

admin = Admin(name='好玩百宝箱',template_mode='bootstrap3')

# 去除视图中无关紧要的表单
class program_view(ModelView):
    form_columns = ('appid','title','image_url','path')
    column_list = ['appid','title','image_url','path']

class awards_view(ModelView):
    form_columns = ('awardId','awardTitle')
    column_list = ['awardId','awardTitle']


admin.add_view(program_view(Program_messages,db.session,name='小程序信息'))
admin.add_view(awards_view(Awards,db.session,name='奖品信息'))
admin.add_view(ModelView(Gift,db.session,name='精品礼包'))
admin.add_view(ModelView(Share,db.session,name='游戏分享'))
admin.add_view(ModelView(Sharecontent,db.session,name='盒子分享库'))
admin.add_view(ModelView(ChannelTongji,db.session,name='统计渠道'))
# admin.add_view(click_num(ClickNubmer,db.session,name='统计点击数'))

# 只读表单模式
# class click_num(ModelView):
#     form_widget_args = {
#         'appid': {
#             'readonly': True
#         },
#         'title': {
#             'readonly': True
#         },
#         'ClickNumbers': {
#             'readonly': True
#         }
#     }
