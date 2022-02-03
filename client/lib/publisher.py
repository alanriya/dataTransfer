import pika
import json
import os
import sys
sys.path.append(os.getcwd())
class DisplayPublisher:
    def __init__(self, config: dict) -> None:
        self.user = config.get("user")
        self.password = config.get("password")
        self.host = config.get("host")
        self.port = config.get("port")
        self.virtual_host = config.get("virtual_host")
        self.exchange = config.get("exchange")
        self.routing_key = config.get("routing_key") 
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
                            pika.ConnectionParameters(host=self.host,
                            port=self.port,
                            virtual_host=self.virtual_host,
                            credentials = self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="topic",auto_delete = False, durable=True)
        
    
    def reconnect(self) -> None:
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="topic")

    def publish(self, data:dict) -> None:
        self.channel.basic_publish(exchange=self.exchange,
                                routing_key="orderbook", 
                                properties=pika.BasicProperties(
                                    content_type='text/plain', 
                                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE), 
                                body=json.dumps(data), mandatory=True)
