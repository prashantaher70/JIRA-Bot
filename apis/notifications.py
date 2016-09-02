from mongouserorgcollection import get_user_from_db_or_error
from utils.utils import AuthenticationException

issueView = "{}/browse/{}"
profileView = "{}/secure/ViewProfile.jspa?name={}"

event_types = {
    "issue_comment_edited": "edited comment on",
    "issue_comment_deleted": "deleted one of the comment on",
    "issue_closed": "closed",
    "issue_commented": "commented on",
    "issue_created": "created",
    "issue_deleted": "deleted",
    "issue_moved": "moved",
    "issue_reopened": "reopened",
    "issue_resolved": "resolved",
    "issue_updated": "updated",
    "issue_worklogged": "logged work on",
    "issue_workstarted": "started work on",
    "issue_workstopped": "stopped working on",
}

def process_event(user_id, event):
    processed_event = {}
    user = get_user_from_db_or_error(user_id)

    processed_event["timestamp"] = event["timestamp"]

    processed_event["user"] = dict()
    processed_event["user"]["displayName"] = event["user"]["displayName"]
    processed_event["user"]["key"] = event["user"]["key"]
    processed_event["user"]["self"] = profileView.format(user["org"]["endpoint"],
                                                         event["user"]["key"])
    processed_event["user"]["avatar"] = event["user"]["avatarUrls"]["48x48"]

    processed_event["issue"] = dict()
    processed_event["issue"]["key"] = event["issue"]["key"]
    processed_event["issue"]["summary"] = event["issue"]["key"] + " : " + event["issue"]["fields"]["summary"]
    processed_event["issue"]["self"] = issueView.format(user["org"]["endpoint"],
                                                        event["issue"]["key"])

    type = event_types.get(event["issue_event_type_name"])
    if type:
        processed_event["action"] = type
    else:
        processed_event["action"] = "updated"

    changelogobj = event.get("changelog")
    changelog = None
    if changelogobj:
        changelog = changelogobj.get("items")

    if changelog and len(changelog) == 1:
        if not changelog[0]["toString"]:
            processed_event["action"] = "removed " + changelog[0]["field"] + " of"
        else:
            processed_event["action"] = "updated " + changelog[0]["field"] + " of"
            processed_event["object"] = "to " + changelog[0]["toString"]

    elif changelog and len(changelog) > 1:
        processed_event["action"] = "updated " + str(len(changelog)) + " fields of"
        processed_event["changelog"] = changelog

    comment = event.get("comment")

    if comment:
        processed_event["comment"] = dict()
        processed_event["comment"]["body"] = event["comment"]["body"]

    return processed_event