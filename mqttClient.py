import paho.mqtt.client as mqtt
from principal import AGENT_REGISTRY

class MqttClient:
    def __init__(self, agents):
        self.agents = [agent() for agent in AGENT_REGISTRY]
        self.client = mqtt.Client()

        # Set callback for when a message is received
        self.client.on_message = self.on_message

    def connect(self, broker="localhost", port=1883, topic="test/topic"):
        self.client.connect(broker, port)
        self.client.subscribe(topic)
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"Message received: {message}")

        # Check each agent to see if it evaluates to True for the received message
        for agent in self.agents:
            if agent.evaluate(message):
                agent.execute(message)

    def publish(self, topic, message):
        self.client.publish(topic, message)
