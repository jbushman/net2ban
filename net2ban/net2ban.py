#!/usr/bin/env python
#
# Net2Ban
#

import pika
import ssl

class InvalidParams(Exception): pass

class Net2Ban(object):

        def __init__ ( self , username='none', password='none', host='none', port=5671, queue='none', exchange='none', exchange_type='none', virtual_host='none', ssl=1 ):
                self.username = username
                self.password = password
                self.host = host
                self.port = port
                self.queue = queue
                self.exchange = exchange
                self.exchange_type = exchange_type
                self.virtual_host = virtual_host
                self.ssl = ssl


        def connect ( self ):
                """
                Connects to RabbitMQ server
                """
                self.credentials = pika.PlainCredentials(self.username,
                                                         self.password)

                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                                    port=int(self.port),
                                                                                    virtual_host=self.virtual_host,
                                                                                    credentials=self.credentials,
                                                                                    ssl=bool(self.ssl)))

                self.channel=self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange,
                                         exchange_type=self.exchange_type)
                self.result=self.channel.queue_declare(exclusive=True)
                self.queue_name=self.result.method.queue
                self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name)


        def disconnect ( self ):
                """
                Disconnects from RabbitMQ server
                """
                self.connection.close()


        def write ( self , msg ):
                """
                Sends a message to the queue
                """
                self.channel.basic_publish ( exchange = self.exchange , routing_key = self.queue , body = msg , properties = pika.BasicProperties ( delivery_mode = 2 ) )


        def start_read ( self , callback ):
                """
                Declares a callback function to receive messages
                """
                self.channel.queue_declare ( queue = self.queue , durable = True )
                self.channel.basic_qos ( prefetch_count = 1 )
                self.channel.basic_consume ( callback , queue = self.queue )
                self.channel.start_consuming()

