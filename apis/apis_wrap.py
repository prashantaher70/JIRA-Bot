import json

import oauth2 as oauth

import config as conf
from context import usercontext
from encryption import SignatureMethod_RSA_SHA1
from utils.utils import OmniWheelException, AuthenticationException



def with_auth(api_url, method='GET'):
    """
     body for POST is in kwargs as body
    :param api_url:
    :param method:
    :return:
    """
    def f_wrap(f):
        def func_wrap(*args, **kwargs):
            user = usercontext.user

            if not user:
                raise AuthenticationException('User context not set. Not logged in')

            if not user.get('org'):
                raise AuthenticationException('No organisation found')

            if not user.get('org').get('endpoint'):
                raise AuthenticationException('No endpoint found, configuration needed')

            if not user.get('access_token'):
                raise AuthenticationException('Not authorised')

            access_token = user['access_token']

            consumer = oauth.Consumer(conf.consumer_key, conf.consumer_secret)

            accessToken = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
            client = oauth.Client(consumer, accessToken)
            client.set_signature_method(SignatureMethod_RSA_SHA1())

            org_jira_end = user['org']['endpoint']

            qparams = []
            qparams.append(org_jira_end)
            passed_params = [str(param) for param in args[:]]

            qparams.extend(passed_params)

            api_endpoint = api_url.format(*qparams)

            if method == 'GET':
                resp, content = client.request(api_endpoint, 'GET')
            elif method == 'POST':
                body = kwargs.get('body')
                body_str = json.dumps(body)
                resp, content = client.request(api_endpoint, method='POST', body=body_str, headers= {
                    'Content-Type': 'application/json'
                })
            else:
                raise OmniWheelException('Method type not supported')

            if resp['status'] == '401':
                raise AuthenticationException('Not authorised')

            if resp['status'] != '200' and resp['status'] != '201':
                print "Invalid response %s: %s" % (resp['status'],  content)
                raise OmniWheelException("Failed to process request")

            return json.loads(str(content))

        return func_wrap
    return f_wrap