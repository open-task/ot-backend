#coding=utf-8
from flask import Flask,request,render_template,session,jsonify
import random, redis, pymongo,time
from werkzeug import secure_filename
import os
from testModel import *


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)

client = pymongo.MongoClient('127.0.0.1', 27017)

skill_db = client.open_task.skill
user_db = client.open_task.user

def new_line(db_name):
    dic = {}
    up_no = redis_db.incr(db_name + "_number")
    timestamp = int(time.time())
    dic["id"] = up_no
    dic["create_time"] = timestamp
    dic["update_time"] = timestamp
    dic['state'] = True
    return dic


redis_db = redis.StrictRedis(host='localhost', port=6379)
def insert_cover(db_name, dic):
    up_no = redis_db.incr(db_name + "_number")
    timestamp = int(time.time())
    dic["id"] = up_no
    dic["create_time"] = timestamp
    dic["update_time"] = timestamp
    dic['state'] = True
    return dic

# 技能列表展示页
@app.route("/skill/list_skills",methods=["POST"])
def list_skills():
    skills = list(skill_db.find({"state":True},{"_id":False}).sort("count",-1))
    return jsonify({"state":True,"skills":skills})

@app.route("/skill/skills_get_users",methods=["GET","POST"])
def get_users():
    skill = request.json.get("skill")
    user_list = list(user_db.find({"skill":skill},{"_id":False}))
    for x in user_list:
        address = x['address']
        solutions = Solution().select().where(Solution.solver==address)
        x['solved'] = len(solutions)
    # 这里缺少历史记录
    return jsonify({"state":True,'user_list':user_list})
    
# 用户设置页面
@app.route("/skill/update_user_info",methods=["GET","POST"])
def update_user_info():
    address = request.json.get('address')
    print address
    skills = request.json.get('skill')
    email = request.json['email']
    user_info = user_db.find_one({'address':address})
    if skills:
        if user_info:
            user_skill_in_db = user_info['skill']
        else:
            user_skill_in_db = []
        skill_old = [x for x in user_skill_in_db]
        skill_new = skills
        skill_add = [x for x in skill_new if x not in skill_old]
        skill_del = [x for x in skill_old if x not in skill_new]
        print skill_del
        skill_db.update_many({'name':{"$in":skill_del}},{"$inc":{"count":-1}})
        for name in skill_add:
            update_info = skill_db.update_one({'name':name},{"$setOnInsert":new_line('task_skill'),"$inc":{"count":1}},upsert=True)
            

    user_db.update({'address':address},{"$set":{"skill":skills,'email':email},'$setOnInsert':dict(new_line('task_user').items() + {"address":address}.items())},upsert=True)
    return jsonify({"state":True})


    


@app.route("/skill/get_user_info",methods=["GET","POST"])
def get_user_info():
    address = request.json.get('address')
    user_info = user_db.find_one({"address":address},{"_id":False})
    return jsonify({"state":True,"user_info":user_info})


    









if __name__ == "__main__":
    app.run(debug=True,port=5236,host="0.0.0.0")
