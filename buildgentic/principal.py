
import paho.mqtt.client as mqtt
import os
import importlib
from dotenv import load_dotenv

from buildgentic import agents
from buildgentic.mqtt_client import MqttClient
from buildgentic.registry import get_registered_agents

load_dotenv()


MQTT_BROKER_HOSTNAME=os.getenv("MQTT_BROKER_HOSTNAME")
MQTT_BROKER_PORT=os.getenv("MQTT_BROKER_PORT")
MQTT_BROKER_TOPIC=os.getenv("MQTT_BROKER_TOPIC")


def load_agents_from_directory(directory="agents"):
    """Dynamically import all agent modules from a directory."""

    print(os.path.realpath(directory))

    for filename in os.listdir(directory):
        print(filename)
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"buildgentic.agents.{filename[:-3]}"
            print(module_name)
            importlib.import_module(module_name)

def startup():
    print("starting startup...")


    # Load all agent files dynamically
    load_agents_from_directory(directory=os.path.dirname(agents.__file__))

    # Create the MQTT client with the registered agents
    mqtt_client = MqttClient(agents=get_registered_agents())

    # Connect and subscribe to a topic
    mqtt_client.connect(broker=MQTT_BROKER_HOSTNAME, port=MQTT_BROKER_PORT, topic=MQTT_BROKER_TOPIC)

    # Example publishing a message
    mqtt_client.publish(MQTT_BROKER_TOPIC, "This is an alert message")
    mqtt_client.publish(MQTT_BROKER_TOPIC, "Short msg")

    # Start an infinite loop that will keep the client alive and listening
    mqtt_client.client.loop_forever()

    print("finalizing startup.")

if __name__ == "__main__":
    startup()
