import api_urls
from apis_wrap import with_auth


@with_auth(api_urls.user_url)
def get_user():
    """
    Won't reach inside
    :param user_id:
    :return:
    """
    pass


@with_auth(api_urls.issue_url)
def get_jira(issue_url):
    pass


@with_auth(api_urls.webhooks, 'POST')
def post_webhook():
    """
    pass body as kwargs
    :param user_id:
    :return:
    """
    pass

@with_auth(api_urls.webhooks)
def get_all_webhook():
    pass

