#coding=utf-8
from flask import Flask,request,render_template,session,jsonify
import random, redis, pymongo,time
from werkzeug import secure_filename
import os,time
from testModel import *
from playhouse.shortcuts import dict_to_model, model_to_dict

app = Flask(__name__)

client = pymongo.MongoClient('127.0.0.1', 27017)

skill_db = client.open_task.skill
user_db = client.open_task.user
task_db = client.open_task.task
message_db = client.open_task.message

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
@app.route("/skill/list_skills",methods=["GET","POST"])
def list_skills():
    f = {"state":True}
    if "s" in request.json:
        name = request.json.get('s')
        f['name'] = {"$options": "$i","$regex":name}

    skills = list(skill_db.find(f,{"_id":False}).sort("count",-1))
    return jsonify({"state":True,"skills":skills})

@app.route("/skill/list_tasks",methods=["GET","POST"])
def list_tasks():
    type_ = request.json.get("type")
    page = request.json.get('page',1)
    page_amount = 10

    if type_=='solved':
        missions = list(Mission().select().where(Mission.solved>0).order_by(-Mission.updatetime).paginate(page, page_amount))
    elif type_ == 'published':
        missions = list(Mission().select().where(Mission.solved==0 , Mission.solution_num==0).order_by(-Mission.updatetime).paginate(page, page_amount))
    elif type_ == 'unsolved':
        missions = list(Mission().select().where(Mission.solved==0 ,Mission.solution_num>0).order_by(-Mission.updatetime).paginate(page, page_amount))
    else:
        missions = list(Mission().select().order_by(-Mission.updatetime).where(1).paginate(page, page_amount))

    database.close()
    missions = sorted([model_to_dict(x) for x in missions],key=lambda s: s['block'],reverse=True)

    for x in missions:
        x['reward'] = str(x['reward'])
    
    return jsonify({"state":True,"missions":missions})
    


@app.route("/skill/skills_get_users",methods=["GET","POST"])
def get_users():
    skill = request.json.get("skill")
    user_list = list(user_db.find({"skill":skill},{"_id":False}))
    for x in user_list:
        address = x['address']
        solutions = Solution().select().where(Solution.solver==address)
        x['solved'] = len(solutions)
    # 这里缺少历史记录
    database.close()
    return jsonify({"state":True,'user_list':user_list})
    
# 用户设置页面
@app.route("/skill/update_user_info",methods=["GET","POST"])
def update_user_info():
    address = request.json.get('address')
    print(address)
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
        skill_db.update_many({'name':{"$in":skill_del}},{"$inc":{"count":-1}})
        for name in skill_add:
            update_info = skill_db.update_one({'name':name},{"$setOnInsert":new_line('task_skill'),"$inc":{"count":1}},upsert=True)
            
    oninsert = new_line('task_user').copy()
    oninsert.update({"address":address})
    user_db.update({'address':address},{"$set":{"skill":skills,'email':email},'$setOnInsert':oninsert},upsert=True)
    return jsonify({"state":True})


@app.route("/skill/add_task",methods=["GET","POST"])
def add_skill():
    skill_old = [x['name'] for x in skill_db.find({})]
    skills = request.json.get('skill')
    id_ = request.json.get("id")
    skill_new = [x for x in skills if x not in skill_old]
    for x in skill_new:
        skill_db.insert(insert_cover("skill",{'name':x,"count":1}))
    task_db.insert(insert_cover("task",{'task_id':id_,"skills":skills}))
    return jsonify({"state":True})
    

@app.route("/skill/get_task_info",methods=["GET","POST"])
def get_task_info():
    id_ = request.json.get("id")
    task = task_db.find_one({'task_id':id_},{"_id":False})
    print(task)
    return jsonify({"state":True,"task":task})
    


@app.route("/skill/get_user_info",methods=["GET","POST"])
def get_user_info():
    address = request.json.get('address')
    user_info = user_db.find_one({"address":address},{"_id":False})
    return jsonify({"state":True,"user_info":user_info})


    
@app.route("/skill/search_task",methods=["GET","POST"])
def search_task():
    q = request.json.get("q")
    page = request.json.get('page',1)
    page_amount = 20
    a = "%"+q+"%" 
    print(a)
    missions = list(Mission().select().order_by(-Mission.updatetime).where(Mission.context  ** str(a)).paginate(page, page_amount))
    missions = sorted([model_to_dict(x) for x in missions],key=lambda s: s['block'],reverse=True)
    for x in missions:
        x['reward'] = str(x['reward'])
    database.close()
    return jsonify({"state":True,"missions":missions})
    
@app.route("/skill/leave_message",methods=["GET","POST"])
def leave_message():
    content = request.json.get('content')
    address = request.json.get('address')
    message_db.insert(insert_cover('message',{'content':content,'address':address}))

    return jsonify({"state":True})
    

@app.route("/skill/get_messages",methods=["GET","POST"])
def get_messages():
    page = request.json.get('page',1)
    page_amount = request.json.get('count',20)

    messages = list(message_db.find({'state':True},{"_id":False}).sort([("id",-1)]).skip(page_amount*(page-1)).limit(page_amount))
    for x in messages:
        x['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(x['create_time']))

    count = message_db.find({'state':True}).count()
    return jsonify({"state":True,"messages":messages,"count":count})
    








if __name__ == "__main__":
    app.run(debug=True,port=5236)
