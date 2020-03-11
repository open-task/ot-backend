#coding=utf-8
from flask import Flask,request,render_template,session,jsonify
import random, redis, pymongo,time
from werkzeug import secure_filename
import os,time,json,re
from testModel import *
from playhouse.shortcuts import dict_to_model, model_to_dict

app = Flask(__name__)

client = pymongo.MongoClient('127.0.0.1', 27017)

skill_db = client.open_task.skill
user_db = client.open_task.user
message_db = client.open_task.message
game_db = client.open_task.game
# 问答相关
question_db = client.open_task.question
answer_db = client.open_task.answer
# 拍卖相关
pai_db = client.open_task.paimai
bid_db = client.open_task.bid

log_db = client.open_task.log


# 任务相关
mission_db = client.open_task.mission
solution_db = client.open_task.solution


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
    type_ = request.json.get("task_state",'all')
    page = int(request.json.get('page',1))-1
    sort_type = request.json.get('sort_type','timestamp')#timestamp,reward
    sort_price = request.json.get('sort_price') #0-1
    filter_ = request.json.get('filter')

    page_amount = int(request.json.get("count",10))
    f = {'state':True}
    if type_ == 'all':
        f['task_state'] = {"$nin":['waiting_chain']}
    else:
        f['task_state'] = type_

    if sort_price:
        price_range = sort_price.split("-")
        f['reward'] = {"$gt":int(price_range[0]),'$lt':int(price_range[1])}
    if filter_:
        f['task_state'] = filter_
    q = request.json.get("q")
    mission_id = request.json.get("mission_id")
    if q:
        f['title'] = {"$options": "$i","$regex":q}
    if mission_id :
        f['missionId'] = mission_id


    missions = list(mission_db.find(f,{"_id":False}).sort(sort_type,-1).limit(page_amount).skip(page*page_amount))
    for x in missions:
        task_id = x['missionId']
        x["solution_count"] = solution_db.find({'missionId':task_id}).count()

    count = mission_db.find(f).limit(9999).count()

    
    return jsonify({"state":True,"missions":missions,"count":count})
    


@app.route("/skill/skills_get_users",methods=["GET","POST"])
def get_users():
    # 通过技能获取用户列表
    skill = request.json.get("skill")
    page = request.json.get('page',1)
    page_size = request.json.get('count',20)
    user_list = list(user_db.find({"skill":skill},{"_id":False}).skip((page-1)*page_size).limit(page_size))
    count = user_db.find({"skill":skill},{"_id":False}).count()
    return jsonify({"state":True,'user_list':user_list,"count":count})

@app.route("/skill/get_user_order",methods=["GET","POST"])
def get_user_order():
    income_id_list = [x["missionId"] for x in solution_db.find({'solution_state':"accept"},{'_id':False})]
    income = list(mission_db.find({'missionId':{"$in":income_id_list}},{"_id":False}))
    paid = list(mission_db.find({"task_state":{"$nin":["waiting_chain"]}},{'_id':False}))
    return jsonify({"state":True,"income":income,'paid':paid})
    

    
# 用户设置页面
@app.route("/skill/update_user_info",methods=["GET","POST"])
def update_user_info():
    address = request.json.get('address')
    skills = request.json.get('skill')

    email = request.json['email']
    self_intro = request.json.get('self_intro',"")
    price = request.json.get('price',"")
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
    user_db.update({'address':address},{"$set":{"skill":skills,'email':email,'self_intro':self_intro,"price":price},'$setOnInsert':oninsert},upsert=True)
    return jsonify({"state":True})


@app.route("/skill/add_task",methods=["GET","POST"])
def add_task():
    skill_old = [x['name'] for x in skill_db.find({})]
    skills = request.json.get('skill')
    print(request.json)
    skill_new = [x for x in skills if x not in skill_old]
    for x in skill_new:
        skill_db.insert_one(insert_cover("skill",{'name':x,"count":1}))
    info = {
        "missionId":request.json.get("id"),
        'title':request.json.get('title'),
        'desc':request.json.get('desc'),
        'skill':skills,
        'author':request.json.get('author'),
        'timestamp':int(time.time()),
        'reward':request.json.get('reward'),
        'task_state':'waiting_chain',
        "fu_type":"task"
        }
    mission_db.insert_one(insert_cover("mission",info))
    return jsonify({"state":True})
    
@app.route("/skill/add_solution",methods=["GET","POST"])
def add_solution():
    id_ =  request.json.get('missionId')
    info = {
        "missionId":id_,
        'solutionId':request.json.get('solutionId'),
        "content":request.json.get('content'),
        'author':request.json.get('author'),
        'timestamp':int(time.time()),
        'solution_state':'waiting_chain',
        'fn_type':"task"
        }
    solution_db.insert_one(insert_cover('solution',info))
    mission_db.update({"missionId":id_},{"$set":{"task_state":"updated"}})
    return jsonify({"state":True})
    

@app.route("/skill/get_task_info",methods=["GET","POST"])
def get_task_info():
    id_ = request.json.get("id")
    task = mission_db.find_one({'missionId':id_},{"_id":False})
    solutions = list(solution_db.find({"missionId":id_,'solution_state':{"$in":['published','accept','reject']}},{"_id":False}))
    return jsonify({"state":True,"task":task,"solutions":solutions})
    


@app.route("/skill/get_user_info",methods=["GET","POST"])
def get_user_info():
    address = request.json.get('address')
    user_info = user_db.find_one({"address":address},{"_id":False})
    if not user_info:
        return jsonify({"state":False,"user_info":{}})
    print("user_info",user_info,address)
    # 获取task的信息
    tasks = list(mission_db.find({"author":address},{"_id":False}))
    task_count = len(tasks) #总task数量
    paid = sum([int(x['reward']) for x in tasks])# 这里是总支出
    solutions = list(solution_db.find({'author':address},{"_id":False}))
    solution_count = len(solutions)
    accept_list = [x['missionId'] for x in solutions if x['solution_state']=='accept']
    accept_count = len(accept_list)
    rewards = list(mission_db.find({'missionId':{"$in":accept_list}},{"_id":False}))
    reward = sum([int(x['reward']) for x in rewards])
    print(rewards,accept_list)
    # 获取question的信息
    questions = list(question_db.find({},{"_id":False}))
    answers = list(answer_db.find({},{"_id":False}))
    answer_accept = [x for x in answers if x['answer_state'] == 'accept']

    user_info['task'] = {"task_count":task_count,"solution_count":solution_count,'solution_accept_count':accept_count}
    user_info['question'] = {'question_count':len(questions),'answer_count':len(answers),'answer_accept_count':len(answer_accept)}
    user_info["paid"] = paid
    user_info["reward"] = reward



    return jsonify({"state":True,"user_info":user_info})


    
@app.route("/skill/search_task",methods=["GET","POST"])
def search_task():
    q = request.json.get("q")
    page = request.json.get('page',1)
    page_amount = 20
    a = "%"+q+"%" 
    print(a)
    missions = list(Mission().select().order_by(-Mission.updatetime).where(Mission.context  ** str(a),Mission.filter==0).paginate(page, page_amount))
    missions = sorted([model_to_dict(x) for x in missions],key=lambda s: s['block'],reverse=True)
    for x in missions:
        x['reward'] = str(x['reward'])
    database.close()
    return jsonify({"state":True,"missions":missions})
    
@app.route("/skill/leave_message",methods=["GET","POST"])
def leave_message():
    content = request.json.get('content')
    address = request.json.get('address')
    message_db.insert_one(insert_cover('message',{'content':content,'address':address,'reply':""}))

    return jsonify({"state":True})
    

@app.route("/skill/get_messages",methods=["GET","POST"])
def get_messages():
    page = request.json.get('page',1)
    page_amount = request.json.get('count',20)

    messages = list(message_db.find({'state':True},{"_id":False}).sort([("id",-1)]).skip(page_amount*(page-1)).limit(page_amount))
    for x in messages:
        x['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(x['create_time']))
        x['reply'] = x.get("reply","")
    count = message_db.find({'state':True}).count()
    return jsonify({"state":True,"messages":messages,"count":count})
    

@app.route("/skill/add_game_card",methods=["GET","POST"])
def add_game_card():
    info = request.json.get('info')
    game_db.insert_one(insert_cover('game_exchange',info))
    return jsonify({"state":True})
    

@app.route("/skill/get_game_card",methods=["GET","POST"])
def get_game_card():
    info = list(game_db.find({},{"_id":False}).sort([("id",-1)]))
    for x in info:
        str_len = len(x['contact'])
        if str_len>3:
            inter = int(str_len/3)
            contact = x['contact']
            contact = contact[0:inter]+"****"+contact[(-1*inter):]
            x['contact'] = contact
        else:
            x['contact'] = "***"
    return jsonify({"state":True,"info":info})
    


# 问答模块

# 创建问答
@app.route("/question/new_question",methods=["GET","POST"])
def new_question():
    key_list = ['address','title','content','reward',"missionId"]
    info = {
        'question_state':"waiting_chain",
        'fn_type':"question"
    }
    for x in key_list:
        info[x] = request.json.get(x)
    ins = insert_cover('question',info)
    q_id = ins["id"]
    q = question_db.insert_one(ins)
    
    return jsonify({"state":True,'question_id':q_id})

# 获取单个问题

@app.route("/question/get_question",methods=["GET","POST"])
def get_question():
    print(request.json)
    question_id = request.json.get("question_id")
    q = question_db.find_one({'missionId':question_id,'state':True},{"_id":False})
    if q['question_state']=="waiting_chain":
        return jsonify({"state":False,'msg':"项目还在发行中，请稍后重试"})
    answers = list(answer_db.find({'missionId':question_id,'state':True,'answer_state':{"$nin":['waiting_chain']}},{"_id":False}))
    q['answers'] = answers

    return jsonify({"state":True,'question':q})

# 获取问答列表
@app.route("/question/get_question_list",methods=["GET","POST"])
def get_question_list():
    page_size = request.json.get('count',20)
    page = request.json.get('page',1)-1
    info = {'state':True}
    sort_type = request.json.get('sort_type','timestamp')#timestamp,reward
    sort_price = request.json.get('sort_price') #0-1
    filter_ = request.json.get('filter')
    if sort_type=="timestamp":
        sort_type ="update_time"
    reward_section = request.json.get("reward_section",None)
    if reward_section:
        reward_section = reward_section.split('-')
        info['reward'] = {"$gt":reward_section[0],'$lt':reward_section[1]}
    question_state = request.json.get("question_state",None)
    if question_state:
        info['question_state'] = question_state
    else:
        info['question_state'] = {"$nin":['waiting_chain',""]}

    if sort_price:
        price_range = sort_price.split("-")
        info['reward'] = {"$gt":int(price_range[0]),'$lt':int(price_range[1])}
    if filter_:
        info['task_state'] = filter_

    q = request.json.get("q")
    mission_id = request.json.get("mission_id")
    if q:
        info['title'] = {"$options": "$i","$regex":q}
    if mission_id :
        info['missionId'] = mission_id

    print(info)
    q = list(question_db.find(info,{"_id":False}).limit(page_size).skip(page*page_size).sort(sort_type,-1))
    for x in q:
        q_id = x['missionId']
        a_list = list(answer_db.find({'missionId':q_id,'state':True}))
        x['answer_amount'] = len(a_list)

    count = question_db.find(info).count()
    return jsonify({"state":True,'question':q,'count':count})

# 提交答案
@app.route("/question/answer",methods=["GET","POST"])
def answer():
    info = {
        
        "missionId":str(request.json.get('missionId')),
        "content":request.json.get('content'),
        'timestamp':int(time.time()),
        'author':request.json.get('author'),
        'answer_state':'waiting_chain',
        'fn_type':"question"
    }
    to_insert = insert_cover('answer',info)
    a_id = to_insert.get('id')
    a = answer_db.insert_one(to_insert)

    return jsonify({"state":True,'answer_id':a_id})
    
# 接受答案,好像只能通过线上确认


# 币名拍卖
@app.route("/skill/get_coin_name_list",methods=["GET","POST"])
def get_coin_name_list():
    coin_list = list(pai_db.find({"state":True},{'_id':False}))
    return jsonify({"state":True,"coin":coin_list})

@app.route("/skill/get_coin_info",methods=["GET","POST"])
def get_coin_info():
    name = request.json.get("name")
    coin_info = pai_db.find_one({'name':name},{"_id":False})
    bid_list = list(bid_db.find({'pai_id':coin_info['id'],'state':True},{"_id":False}).sort('charge',-1))
    for x in bid_list:
        str_len = len(x['contact'])
        if str_len>3:
            inter = int(str_len/3)
            contact = x['contact']
            contact = contact[0:inter]+"****"+contact[(-1*inter):]
            x['contact'] = contact
        else:
            x['contact'] = "***"
    price_max =bid_list[0]['charge'] if len(bid_list) else coin_info['basic']
    coin_info['max'] = price_max
    return jsonify({"state":True,'coin_info':coin_info,'bid_list':bid_list})
    

@app.route("/skill/pai",methods=["GET","POST"])
def pai():
    name = request.json.get("name")
    c = pai_db.find_one({'name':name},{"_id":False})
    pai_id = c['id']
    info = {'name':c['name'],'basic':c['basic'],'pai_id':pai_id}
    key_list = ['charge','contact_type','contact','rise']
    for x in key_list:
        info[x] = request.json.get(x)

    bid_db.insert_one(insert_cover('bid',info))
    return jsonify({"state":True})
    

@app.route("/skill/add_log",methods=["GET","POST"])
def add_log():
    print('添加日志')
    info_list = json.loads(request.form.get("log_list"))
    try:
        max_id = int(redis_db.get('block_number'))
    except:
        max_id = 0
    t = 0
    


    # max_id = 15795790
    useful_info = sorted([x for x in info_list if int(x['block_number']) > max_id],key=lambda a:a['block_number'])
    # useful_info = info_listist
    publish = [x for x in useful_info if x['fn_name'] == 'publish']
    accept = [x for x in useful_info if x['fn_name'] == 'accept']
    reject = [x for x in useful_info if x['fn_name'] == 'reject']
    solve = [x for x in useful_info if x['fn_name'] == 'solve']


    m_id = 0
    for x in publish:
        # print(x)
        fn_type = x['data']['data'].get("fn_type",'task')
        if fn_type == "task":
            missionId = x['data']['missionId']
            mission_db.update_one({"missionId":missionId,"task_state":"waiting_chain"},{"$set":{"task_state":"published"}})
        if fn_type == "question":
            # print(x)
            missionId = x['data']['missionId']
            question_db.update_one({"missionId":missionId,"question_state":"waiting_chain"},{"$set":{"question_state":"published"}})
            # 将上chanin的数据改为waiting
    for x in solve:
        # print('Solve',x)
        fn_type = x['data']['data'].get("fn_type",'task')
        if fn_type == "task":
            missionId = x['data']['missionId']
            solutionId = x['data']['solutionId']
            solution_db.update_one({"missionId":missionId,'solutionId':solutionId,"solution_state":"waiting_chain"},{"$set":{"solution_state":"published"}})
        if fn_type == "question":
            missionId = str(x['data']['data']['missionId'])
            solutionId = int(x['data']['data']['solutionId'])
            answer_db.update_one({"missionId":missionId,'id':solutionId,"answer_state":"waiting_chain"},{"$set":{"answer_state":"published"}})
    for x in accept:
        fn_type= x['data'].get("fn_type",'task')
        try:
            solutionId = int(x['data']['solutionId'])
            task = solution_db.find_one({'solutionId':solutionId})
            if task:
                missionId = task['missionId']
                solution_db.update_one({'solutionId':solutionId},{'$set':{'solution_state':"accept"}})
                mission_db.update_one({"missionId":missionId},{"$set":{'solutionId':solutionId,'task_state':"success"}})

            task = answer_db.find_one({'id':solutionId})
            if task:
                missionId = task['missionId']
                answer_db.update_one({'id':solutionId},{'$set':{'answer_state':"accept"}})
                question_db.update_one({"missionId":missionId},{"$set":{'answerId':solutionId,'question_state':"success"}})
        except:
            print("ACCEPT错误",x)
    for x in reject:
        fn_type= x['data'].get("fn_type",'task')
        solutionId = int(x['data']['solutionId'])
        solution_db.update_one({'solutionId':solutionId},{'$set':{'solution_state':"reject"}})
        answer_db.update_one({'id':solutionId},{'$set':{'answer_state':"reject"}})


    id_list= [x['block_number'] for x in useful_info]
    for x in useful_info:
        log_db.insert_one(x)
        t+=1
        redis_db.set("block_number",int(x['block_number']))

    return jsonify({"state":True})
    



if __name__ == "__main__":
    app.run(debug=True,port=5236)








