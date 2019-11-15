dic = [{'name': 'MIOTA', 'basic': 2000},
 {'name': 'PAXOS', 'basic': 2000},
 {'name': 'STEEM', 'basic': 2000},
 {'name': 'THETA', 'basic': 2000},
 {'name': 'WAVES', 'basic': 2000},
 {'name': 'ALPHA', 'basic': 2000},
 {'name': 'ANGEL', 'basic': 2000},
 {'name': 'ANKLE', 'basic': 2000},
 {'name': 'BLOOD', 'basic': 2000},
 {'name': 'BONUS', 'basic': 2000},
 {'name': 'BOOTY', 'basic': 2000},
 {'name': 'CACHE', 'basic': 2000},
 {'name': 'CANDY', 'basic': 2000},
 {'name': 'CLOCK', 'basic': 2000},
 {'name': 'CLOWN', 'basic': 2000},
 {'name': 'CRACK', 'basic': 2000},
 {'name': 'CRANE', 'basic': 2000},
 {'name': 'DEMON', 'basic': 2000},
 {'name': 'DEVIL', 'basic': 2000},
 {'name': 'FRONT', 'basic': 2000},
 {'name': 'GLOOM', 'basic': 2000},
 {'name': 'GLORY', 'basic': 2000},
 {'name': 'GRACE', 'basic': 2000},
 {'name': 'GRADE', 'basic': 2000},
 {'name': 'GRANT', 'basic': 2000},
 {'name': 'GREAT', 'basic': 2000},
 {'name': 'GREET', 'basic': 2000},
 {'name': 'HEART', 'basic': 2000},
 {'name': 'HOBBY', 'basic': 2000},
 {'name': 'HOBOS', 'basic': 2000},
 {'name': 'HOKEY', 'basic': 2000},
 {'name': 'HONER', 'basic': 2000},
 {'name': 'HONEY', 'basic': 2000},
 {'name': 'HOUSE', 'basic': 2000},
 {'name': 'JAGER', 'basic': 2000},
 {'name': 'JAGGY', 'basic': 2000},
 {'name': 'JEWEL', 'basic': 2000},
 {'name': 'KEFIR', 'basic': 2000},
 {'name': 'KEIRS', 'basic': 2000},
 {'name': 'LAKER', 'basic': 2000},
 {'name': 'LARGE', 'basic': 2000},
 {'name': 'LEAST', 'basic': 2000},
 {'name': 'LEAVE', 'basic': 2000},
 {'name': 'LEDGE', 'basic': 2000},
 {'name': 'LEDGY', 'basic': 2000},
 {'name': 'LEECH', 'basic': 2000},
 {'name': 'LEERY', 'basic': 2000},
 {'name': 'LEGAL', 'basic': 2000},
 {'name': 'LEGGY', 'basic': 2000},
 {'name': 'LEGIT', 'basic': 2000},
 {'name': 'LEMON', 'basic': 2000},
 {'name': 'MOODY', 'basic': 2000},
 {'name': 'MOTTO', 'basic': 2000},
 {'name': 'NIGHT', 'basic': 2000},
 {'name': 'OASIS', 'basic': 2000},
 {'name': 'OCEAN', 'basic': 2000},
 {'name': 'OMEGA', 'basic': 2000},
 {'name': 'OTHER', 'basic': 2000},
 {'name': 'OUTER', 'basic': 2000},
 {'name': 'PEARL', 'basic': 2000},
 {'name': 'SEVEN', 'basic': 2000},
 {'name': 'SHINE', 'basic': 2000},
 {'name': 'SMALL', 'basic': 2000},
 {'name': 'SMART', 'basic': 2000},
 {'name': 'SPELL', 'basic': 2000},
 {'name': 'SPORT', 'basic': 2000},
 {'name': 'START', 'basic': 2000}]



import random, redis, pymongo,time
import requests

client = pymongo.MongoClient('127.0.0.1', 27017)

pai_db = client.open_task.paimai



redis_db = redis.StrictRedis(host='localhost', port=6379)
def insert_cover(db_name, dic):
    up_no = redis_db.incr(db_name + "_number")
    timestamp = int(time.time())
    dic["id"] = up_no
    dic["create_time"] = timestamp
    dic["update_time"] = timestamp
    dic['state'] = True
    return dic

for  x in dic:
	if not pai_db.find_one({'name':x['name']}):
		pai_db.insert_one(insert_cover("pai",x))



