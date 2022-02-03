import pika
import sys, os
import json
from lib.orderbookManager import OrderBookManager

sys.path.append(os.getcwd())

class Consumer:
    def __init__(self, config: dict) -> None:
        self.user = config.get("user")
        self.password = config.get("password")
        self.host = config.get("host")
        self.port = config.get("port")
        self.virtual_host = config.get("virtual_host")
        self.exchange = config.get("exchange")
        self.routing_key = config.get("routing_key")
        self.queue_name = config.get("queue")

        self.orderbookManager = OrderBookManager()
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
                            pika.ConnectionParameters(host=self.host,
                            port=self.port,
                            virtual_host=self.virtual_host,
                            credentials = self.credentials)) 
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.queue_bind(exchange=self.exchange , queue =self.queue_name, routing_key=self.routing_key)

    def onMessage(self, ch, method, properties, body) -> None:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        self.orderbookManager.add(json.loads(body))
        
    def start_consuming(self)->None:
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.onMessage)
        self.channel.start_consuming()

