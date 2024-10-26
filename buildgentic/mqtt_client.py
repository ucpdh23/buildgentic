import paho.mqtt.client as mqtt

class MqttClient:
    def __init__(self, agents):
        self.agents = agents
        self.client = mqtt.Client()
        self.debugging = True

        # Set callback for when a message is received
        self.client.on_message = self.on_message

    def connect(self, broker="localhost", port=1883, topic="test/topic"):
        if (self.debugging): print("connecting to", broker, port, "...")
        self.client.connect(host=broker, port=port)
        if (self.debugging): print("subscribing...")
        self.client.subscribe(topic)
        if (self.debugging): print("loop starting...")
        self.client.loop_start()
        print("connected")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        if (self.debugging): print(f"Message received: {message}")

        # Check each agent to see if it evaluates to True for the received message
        for agent in self.agents:
            if agent.evaluate(message):
                agent.execute(message)

    def publish(self, topic, message):
        if (self.debugging): print("publishing message", topic, message)
        self.client.publish(topic, message)
