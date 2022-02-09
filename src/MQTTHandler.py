import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT


class MQTTHandler:

    def connect(mqtt_client, userdata, flags, rc):
        # This function will be called when the mqtt_client is connected
        # successfully to the broker.
        print("Connected to MQTT Broker!")
        print(f'Flags: {flags}; RC: {rc}')

    def disconnect(self, mqtt_client, userdata, rc):
        # This method is called when the mqtt_client disconnects
        # from the broker.
        print("Disconnected from MQTT Broker!")

    def subscribe(mqtt_client, userdata, topic, granted_qos):
        # This method is called when the mqtt_client subscribes to a new feed.
        print(f'Subscribed to {topic} with QOS level {granted_qos}')

    def unsubscribe(mqtt_client, userdata, topic, pid):
        # This method is called when the mqtt_client unsubscribes from a feed.
        print(f'Unsubscribed from {topic} with PID {pid}')

    def publish(mqtt_client, userdata, topic, pid):
        # This method is called when the mqtt_client publishes data to a feed.
        print(f'Published to {topic} with PID {pid}')

    def message(client, topic, message):
        # Method called when a client's subscribed feed has a new value.
        print(f'New message on topic {topic}: {message}')

    def __init__(self, broker, port, username, password):
        # Create a socket pool
        pool = socketpool.SocketPool(wifi.radio)

        # Set up a MiniMQTT Client
        self.mqtt_client = MQTT.MQTT(
            broker=broker,
            port=port,
            username=username,
            password=password,
            socket_pool=pool,
            ssl_context=ssl.create_default_context(),
        )

        # Connect callback handlers to mqtt_client
        self.mqtt_client.on_connect = MQTTHandler.connect
        self.mqtt_client.on_disconnect = MQTTHandler.disconnect
        self.mqtt_client.on_subscribe = MQTTHandler.subscribe
        self.mqtt_client.on_unsubscribe = MQTTHandler.unsubscribe
        self.mqtt_client.on_publish = MQTTHandler.publish
        self.mqtt_client.on_message = MQTTHandler.message

        print(f'Attempting to connect to {broker}')
        self.mqtt_client.connect()

    def get_client(self):
        return self.mqtt_client