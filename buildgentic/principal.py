
import paho.mqtt.client as mqtt
import os
import importlib
from dotenv import load_dotenv

from buildgentic import agents
from buildgentic.mqtt_client import MqttClient
from buildgentic.registry import build_registered_agents

import json

load_dotenv()


MQTT_BROKER_HOSTNAME=os.getenv("MQTT_BROKER_HOSTNAME")
MQTT_BROKER_PORT=os.getenv("MQTT_BROKER_PORT")
MQTT_BROKER_TOPIC=os.getenv("MQTT_BROKER_TOPIC")


def load_agents_from_directory(directory="agents"):
    """Dynamically import all agent modules from a directory."""

    print(os.path.realpath(directory))

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"buildgentic.agents.{filename[:-3]}"
            print(module_name)
            importlib.import_module(module_name)

def startup():
    print("starting startup...")

    # Load all agent files dynamically
    load_agents_from_directory(directory=os.path.dirname(agents.__file__))
    _agents = build_registered_agents()

    # Create the MQTT client with the registered agents
    mqtt_client = MqttClient(agents=_agents)

    # Connect and subscribe to a topic
    mqtt_client.connect(broker=MQTT_BROKER_HOSTNAME, port=int(MQTT_BROKER_PORT), topic=MQTT_BROKER_TOPIC)

    payload = {
        'action': "welcome",
        'message': "buildgentic online :) and ready to work"
    }

    # Example publishing a message
    mqtt_client.publish(MQTT_BROKER_TOPIC, payload)

    for agent in _agents:
        agent.registerInSevant(mqtt_client)

    # Start an infinite loop that will keep the client alive and listening
    mqtt_client.client.loop_forever()

    print("finalizing startup.")

if __name__ == "__main__":
    startup()
