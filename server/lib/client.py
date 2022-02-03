#!/usr/bin/env python
import pika
import sys
import random

counter = 1 
credentials = pika.PlainCredentials('alan', '123')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="192.168.0.111",
                            port=5672,
                            virtual_host="solarity",
                            credentials = credentials))
channel = connection.channel()

# channel.exchange_declare(exchange='topic_logs', exchange_type='topic', auto_delete = False, durable=True)

result = channel.queue_declare(queue='market_message', exclusive=True)
queue_name = result.method.queue
print(queue_name)

# binding_keys = sys.argv[1:]
# if not binding_keys:
#     sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
#     sys.exit(1)

# for binding_key in binding_keys:
channel.queue_bind(
        exchange='topic_logs', queue=queue_name, routing_key="mm")

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, f"{body}"))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=False)

channel.start_consuming()