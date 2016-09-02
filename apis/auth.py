import urlparse

import oauth2 as oauth
import pymongo

import auth_urls
import config as conf
from apis import get_user
from apis_wrap import AuthenticationException, OmniWheelException
from context import usercontext
from encryption import SignatureMethod_RSA_SHA1
from mongouserorgcollection import org_collection, get_user_from_db_or_error, get_org_from_db
from mongouserorgcollection import user_collection
from utils.utils import generate_user_id


def start_auth(org_name, user_id_to_swap=None, configuring=False):
    org_object = org_collection.find_one({
        'name': org_name
    })

    if not org_object:
        raise OmniWheelException('No organisation found')

    if not org_object.get('configured') and not configuring:
        raise OmniWheelException('Organisation not configured. Ask administrator to do so')

    org_jira_end = org_object['endpoint']

    consumer = oauth.Consumer(conf.consumer_key, conf.consumer_secret)
    client = oauth.Client(consumer)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    request_token_url = auth_urls.request_token_url.format(org_jira_end)
    authorize_url = auth_urls.authorize_url.format(org_jira_end)
    resp, content = client.request(request_token_url, 'POST')
    if resp['status'] != '200':
        raise Exception('Invalid response %s: %s' % (resp['status'],  content))

    request_token = dict(urlparse.parse_qsl(content))
    user_auth_url = '%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'])

    swapped = False
    user_id = user_id_to_swap
    if user_id_to_swap:
        result = user_collection.update_one({
            'user_id': user_id_to_swap
        }, {
            "$set": {
                'request_token': request_token,
                'access_token': None,
                'has_authorised': False
            }
        })
        if result.matched_count == 1:
            swapped = True

    if not swapped:
        gen_user_id = str(generate_user_id())
        user_id = gen_user_id
        user_collection.insert_one({
            'request_token': request_token,
            'has_authorised': False,
            'user_id': gen_user_id,
            'org': org_object
        })

    return user_id, user_auth_url


def continue_auth(user_id):
    user = get_user_from_db_or_error(user_id)
    request_token = user['request_token']
    org_jira_end = user['org']['endpoint']

    consumer = oauth.Consumer(conf.consumer_key, conf.consumer_secret)
    token = oauth.Token(request_token['oauth_token'],
                        request_token['oauth_token_secret'])
    client = oauth.Client(consumer, token)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    access_token_url = auth_urls.access_token_url.format(org_jira_end)

    resp, content = client.request(access_token_url, 'POST')
    access_token = dict(urlparse.parse_qsl(content))

    if resp['status'] == '401':
        raise AuthenticationException("Authorise first or token reuse. Start again")

    if resp['status'] != '200':
        raise Exception('Invalid response %s: %s' % (resp['status'],  content))

    user_collection.update_one({
        'user_id': user_id
    }, {
        "$set": {
            'access_token': access_token,
            'has_authorised': True
        }
    })


def sync_self_user():
    user = usercontext.user
    access_token = user['access_token']
    org_name = user['org']['name']

    if not user.get('user'):
        user = get_user()
        user_collection.delete_one({
            'org.name': org_name,
            'user.emailAddress': user['emailAddress']
        })

        user_collection.update_one({
            'user_id': usercontext.userid
        }, {
            "$set": {
                'access_token': access_token,
                'has_authorised': True,
                'user': user
            }
        })


def create_org(org_name, org_jira_end):
    try:
        if org_jira_end.endswith("/"):
            org_jira_end = org_jira_end[0:-1]

        insert_id = org_collection.insert_one({
            'name': org_name,
            'endpoint': org_jira_end,
            'configured': False
        }).inserted_id
    except pymongo.errors.DuplicateKeyError:
        org = get_org_from_db(org_name)
        if org and org.get('configured'):
            raise OmniWheelException('Organisation already registered')

        org_collection.update_one({
            'name': org_name
        }, {
            "$set": {
                'endpoint': org_jira_end
            }
        })
