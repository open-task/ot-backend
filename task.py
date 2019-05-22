#coding=utf-8
from flask import Flask,request,render_template,session,jsonify
import random, redis, pymongo,time
from werkzeug import secure_filename
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)

client = pymongo.MongoClient('127.0.0.1', 27017)

skill_db = client.opentask.skill
user_db = client.open_task.user




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
@app.route("/v1/list_skill",methods=["POST"])
def list_skill():
	skills = skill_db.find({"state":True}).sort("count",-1)
	return jsonify({"state":True,"skills":skills})

@app.route("/get_users",methods=["GET","POST"])
def get_users():
	skill = request.json.get("skill")
	user_list = list(user_db.find({"skills.name":skill},{"_id":False}))
	# 这里缺少历史记录
	return jsonify({"state":True})
	
# 用户设置页面
@app.route("/update_user_info",methods=["GET","POST"])
def update_user_info():
	address = request.json.get('address')
	info = request.json.get('info')
	user_info = user_db.find_one({'address':address})
	if user_info:
		skills_old = [x['name'] for x in user_info['skills']]
		skills_new = info['skills']
		skill_add = [x for x in skills_new if x not in skill_old]
		skill_del = [x for x in skills_old if x not in skill_new]
		skill_db.update_many({'name':{"$in":skill_del}},{"$inc":{"count",-1}})
		for name in skill_add:
			update_info = skill_db.update_one({'name':name},{"$inc":{"count",1}})
			if not update_info['nModified']:
				info = insert_cover("task_skill",{
						"name":name,
						'count':1
					})

	user_db.update({'address':address},{"$set":info,"$setOnInsert":info})
	return jsonify({"state":True})

@app.route("/get_user_info",methods=["GET","POST"])
def get_user_info():
	address = request.json.get('address')
	user_info = user_db.find_one({"address":address},{"_id":False})
	return jsonify({"state":True})


	









if __name__ == "__main__":
	app.run(debug=True,port=5236,host="0.0.0.0")
