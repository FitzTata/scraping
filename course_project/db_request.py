# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instagram']

follows = db.follows

print('Followers:')
for follow in follows.find({'username': 'photochu', 'user_attribute': 'follower'}, {'username_follower': 1}):
    pprint(follow)
print('Followings:')
for follow in follows.find({'username': 'nine.three.photography', 'user_attribute': 'following'}, {'username_following':1}):
    pprint(follow)