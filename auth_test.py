from apis import auth
from apis.apis import post_webhook, get_all_webhook
import json
from apis import jira_service

user = '348cff81-2fa5-46bd-bd70-89e8dbe36abd'
# auth.create_org('OmniWheel', 'https://omniwheel.atlassian.net')
# print auth.start_auth('OmniWheel')
# auth.continue_auth('179f010e-c2f2-4df7-a8f4-ada7d0844cc4')
# print auth.start_auth('OmniWheel', '179f010e-c2f2-4df7-a8f4-ada7d0844cc4')

# post_webhook(user, **{
#     'body':{
#         "name": "my first webhook via rest",
#         "url": "http://www.example.com/webhooks",
#         "events": [
#             "jira:issue_created",
#             "jira:issue_updated"
#         ],
#         "jqlFilter": "Project = JRA AND resolution = Fixed",
#         "excludeIssueDetails" : False
#     }
# })

#print json.dumps(get_all_webhook(user))
#jira_service.register_webhook_if_not_present(user)
