import redis
import json
redis_client = None

REDIS_CLIENT="localhost"
REDIS_PORT=6379

def get_redis_client(host=REDIS_CLIENT, port=REDIS_PORT):
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(host=host, port=port)
    return redis_client


def set_redis(f):
    def with_client(*args,**kwargs):
        kwargs.update({"redis_client":get_redis_client()})
        return f(*args, **kwargs)
    return with_client


@set_redis
def r_publish(value, channels, redis_client=None):
    #redis_client.publish(channels,value)
    if isinstance(value, str):
        redis_client.publish(channels, value)
    else:
        redis_client.publish(channels, json.dumps(value))


@set_redis
def listen_redis(channels, return_data=True, redis_client=None):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channels)
    # return pubsub.listen()
    listener = pubsub.listen()

    def _generator():
        for item in listener:
            if item["type"] == "subscribe":
                continue
            item_data = item["data"]
            if isinstance(item_data, (str,buffer)):
                item_data = json.loads(item_data)
            if return_data:
                yield item_data
            else:
                item["data"] = item_data
                yield item
    return _generator()