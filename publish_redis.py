from database.bus_redis_client import RedisBusClient
import json

client = RedisBusClient().get_redis_client()


# prepare the content of the message to be published
message_content = {"type": "tokenCreate",
                   "message": "This is an LP_SYSTEM_Notice"}

# publish the message to the specified channel
client.publish("LP_SYSTEM_Notice", json.dumps(message_content))

# print a log indicating that the message has been published
print(f"Published message to 'LP_SYSTEM_Notice': {message_content}")
