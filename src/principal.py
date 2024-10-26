
import paho.mqtt.client as mqtt
import os
import importlib
from dotenv import load_dotenv

load_dotenv()

from mqtt_client import MqttClient
from registry import get_registered_agents

MQTT_BROKER_HOSTNAME=os.getenv("MQTT_BROKER_HOSTNAME")
MQTT_BROKER_PORT=os.getenv("MQTT_BROKER_PORT")
MQTT_BROKER_TOPIC=os.getenv("MQTT_BROKER_TOPIC")


def load_agents_from_directory(directory="agents"):
    """Dynamically import all agent modules from a directory."""
    for filename in os.listdir(directory):
        print(filename)
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{directory}.{filename[:-3]}"  # Strip .py
            print(module_name)
            importlib.import_module(module_name)


if __name__ == "__main__":
    print("starting...")

    # Load all agent files dynamically
    load_agents_from_directory()

    # Create the MQTT client with the registered agents
    mqtt_client = MqttClient(agents=get_registered_agents())

    # Connect and subscribe to a topic
    mqtt_client.connect(broker=MQTT_BROKER_HOSTNAME, port=MQTT_BROKER_PORT, topic=MQTT_BROKER_TOPIC)

    # Example publishing a message
    mqtt_client.publish(MQTT_BROKER_TOPIC, "This is an alert message")
    mqtt_client.publish(MQTT_BROKER_TOPIC, "Short msg")

    # Start an infinite loop that will keep the client alive and listening
    mqtt_client.client.loop_forever()