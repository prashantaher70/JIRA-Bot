from flask import Flask, request, Response

import apis.mongouserorgcollection as mongo
from utils.collectionutils import safe_get_value
from utils.redis_utils import r_publish
from apis.mongouserorgcollection import user_collection

listener = Flask(__name__)

@listener.route('/webhook/<webhook_id>',methods=['POST'])
def webhook_trigger(webhook_id):
    process_webhook_event(webhook_id, request.json)
    return Response('{}', status=200, mimetype='application/json')


def process_webhook_event(webhook_id, event):
        org = get_intended_org(webhook_id)
        org.pop("_id", None)

        users = get_intended_users(event, org)

        event['forUsers'] = users
        event['org'] = org
        notify(org, users, event)
        store(org, event)


def get_intended_org(webhook_id):
    org = mongo.org_collection.find_one({
        'webhook_id': webhook_id.strip()
    })

    return org


def get_intended_users(event, org):
    intendedUsers = set()
    #intended user fields: issue.fields.assignee.key, issue.fields.creator.key, issue.fields.reporter.key
    #TODO: query  issue.fields.watches.self and find watchers

    assignee = safe_get_value(event, 'issue.fields.assignee.key')
    if assignee:
        intendedUsers.add(assignee)

    creator = safe_get_value(event, 'issue.fields.creator.key')
    if creator:
        intendedUsers.add(creator)

    reporter = safe_get_value(event, 'issue.fields.reporter.key')
    if reporter:
        intendedUsers.add(reporter)

    users = user_collection.find({
        "user.key": {
            "$in": list(intendedUsers)
        },
        "org.name": org["name"]
    }, {'user_id': 1, 'user.key': 1, '_id': 0})
    return list(users)


def store(org, event):
    collection = mongo.db[org['name'] + '_notifs']
    collection.insert_one(event)


def notify(org, users, event):
    for user in users:
        r_publish(event, str(user["user_id"]) )


listener.run(host='0.0.0.0', port=80)
