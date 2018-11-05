from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class Program_messages(db.Model):
    __tablename__ = 'program_messages'
    id = db.Column(db.Integer,primary_key=True)
    appid = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    path = db.Column(db.String(200))
    title = db.Column(db.String(50))
    click_numbers = db.Column(db.Integer,default=0)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

# 用户和奖品表的关系表
# user_awards = db.Table('user_awards',
#                        db.Column('awards_id',db.Integer,db.ForeignKey('awards.id'),primary_key=True),
#                        db.Column('user_messages_id',db.Integer,db.ForeignKey('user_messages.id'),primary_key=True))

class Awards(db.Model):
    __tablename__ = 'awards'
    id = db.Column(db.Integer, primary_key=True)
    awardTitle = db.Column(db.String(100))
    awardId = db.Column(db.Integer)


class User_messages(db.Model):
    __tablename__ = 'user_messages'
    id = db.Column(db.Integer,primary_key=True)
    openId = db.Column(db.String(100))
    gold_numbers = db.Column(db.Integer,default=0)
    # awards = db.relationship("Awards",secondary=user_awards,backref='user_messages')
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class Award_record(db.Model):
    __tablename__ = 'award_record'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.String(100))
    award_id = db.Column(db.Integer)
    award_time = db.Column(db.String(50))


    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class Share(db.Model):
    __tablename__ = 'share'
    id = db.Column(db.Integer,primary_key=True)
    appid = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    path = db.Column(db.String(200))
    title = db.Column(db.Integer)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class Gift(db.Model):
    __tablename__ = 'gift'
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    path = db.Column(db.String(200))
    title = db.Column(db.String(50))

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class ClickNubmer(db.Model):
    __tablename__ = 'clicknumber'
    id = db.Column(db.Integer,primary_key=True)
    sortId = db.Column(db.Integer)
    name = db.Column(db.String(200))
    channel = db.Column(db.String(200))
    cha_clicks = db.Column(db.Integer,default=0)
    clicks = db.Column(db.Integer,default=0)

class Sharecontent(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(150))
    url = db.Column(db.String(200))

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class ChannelTongji(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    channel = db.Column(db.String(100))

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
