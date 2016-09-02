import pymongo
from pymongo import MongoClient

from utils.utils import AuthenticationException

client = MongoClient()

db = client['omniwheel']
org_collection = db['orgs']
user_collection = db['users']

user_collection.create_index([('user_id', pymongo.ASCENDING)], unique=True)

org_collection.create_index([('name', pymongo.ASCENDING)], unique=True)


def get_user_from_db_or_error(user_id):
    user = user_collection.find_one({
        'user_id': str(user_id)
    })

    if not user:
        raise AuthenticationException('No user found')
    return user

def get_org_from_db(org_name):
    org = org_collection.find_one({
        'name': org_name
    })
    return org