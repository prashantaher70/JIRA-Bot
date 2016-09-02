from apis import get_all_webhook, post_webhook
from config import webhook_listener_url
from context import usercontext
from mongouserorgcollection import org_collection, db
from utils.utils import generate_user_id
import pymongo
from notifications import process_event

WEBHOOK_NAME = 'OmniWheel Listener'

body = {
    "name": WEBHOOK_NAME,
    "url": None,
    "events": [
        "jira:issue_created",
        "jira:issue_updated",
        "jira:issue_deleted"
    ]
}


def register_webhook_if_not_present():
    webhooks = get_all_webhook()

    for webhook in webhooks:
        if webhook.get('name') == WEBHOOK_NAME:
            return

    webhook_uuid = generate_user_id()
    webhook_id = str(webhook_uuid)

    body['url'] = webhook_listener_url.format(webhook_id)
    additional_args = {
        'body': body
    }
    post_webhook(**additional_args)

    user = usercontext.user

    org = user['org']['name']

    org_collection.update_one({
        'name': org
    }, {
        "$set": {
            'webhook': body['url'],
            'webhook_id': webhook_id,
            'configured': True
        }
    })


def get_notifications_from_db():
    user = usercontext.user
    notif_collection = db[user["org"]["name"] +"_notifs"]

    notifs = notif_collection.find({
        'forUsers.user_id': user['user_id']
    }, {'_id': 0}).sort("timestamp", pymongo.DESCENDING).limit(20)

    notifs = list(notifs)
    notifs = [process_event(user["user_id"], n) for n in notifs]
    return notifs