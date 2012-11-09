'''
Created on Nov 9, 2012

@author: jasonmarshall
'''
from ethicsapplication.signals import application_created
from review.signals import application_accepted_by_reviewer,\
    application_rejected_by_reviewer
import pika
import json


def lifecycle_event_handler(sender, **kwargs):
    '''
        This handler will send a message to a message queue
        with information about the lifecycle event.
    '''
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='ethics_lifecycle_events',
                             exchange_type='fanout')
    
    
    channel.basic_publish(exchange='ethics_lifecycle_events',
                          routing_key='',
                          body='test message')
    
    connection.close()
        
application_created.connect(lifecycle_event_handler)
application_accepted_by_reviewer.connect(lifecycle_event_handler)
application_rejected_by_reviewer.connect(lifecycle_event_handler)