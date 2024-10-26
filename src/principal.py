
import paho.mqtt.client as mqtt
import os
import importlib

from registry import get_registered_agents


def load_agents_from_directory(directory="agents"):
    """Dynamically import all agent modules from a directory."""
    for filename in os.listdir(directory):
        print(filename)
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{directory}.{filename[:-3]}"  # Strip .py
            print(module_name)
            importlib.import_module(module_name)


class MqttClient:
    def __init__(self):
        # Initialize agents from the global registry
        self.agents = get_registered_agents()
        print("loaded", self.agents)
        
        self.client = mqtt.Client()

        # Set callback for when a message is received
        self.client.on_message = self.on_message

    def connect(self, broker="localhost", port=1883, topic="test/topic"):
        self.client.connect(broker, port)
        self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"Message received: {message}")

        # Check each agent to see if it evaluates to True for the received message
        for agent in self.agents:
            if agent.evaluate(message):
                agent.execute(message)

    def publish(self, topic, message):
        self.client.publish(topic, message)


if __name__ == "__main__":
    print("starting...")

    # Load all agent files dynamically
    load_agents_from_directory()

    # Create the MQTT client with the registered agents
    mqtt_client = MqttClient()

    # Connect and subscribe to a topic
    mqtt_client.connect(broker="192.168.1.2", topic="test/topic")

    # Example publishing a message
    mqtt_client.publish("test/topic", "This is an alert message")
    mqtt_client.publish("test/topic", "Short msg")

    # Start an infinite loop that will keep the client alive and listening
    mqtt_client.client.loop_forever()