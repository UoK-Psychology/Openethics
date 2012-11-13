from ethicsapplication.signals import application_created
from review.signals import application_accepted_by_reviewer,\
    application_rejected_by_reviewer
import pika
import json
from django.conf import settings

def _send_message(host, exchange_info, message, routing=''):
    '''
        This function uses the pika library to send a message to an AMQP queue.
        
        @param host: The AMQP host
        @param exchange_info: a tuple (exchange_name, exchange_type)
        @param message: The message body
        @param routing: (optional) the routing key to use. 
    
    '''
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host))
    channel = connection.channel()
    
    channel.exchange_declare(exchange=exchange_info[0],
                             exchange_type=exchange_info[1])
    
    
    channel.basic_publish(exchange=exchange_info[0],
                          routing_key=routing,
                          body=message)
    
    connection.close()
def lifecycle_event_handler(sender, **kwargs):
    '''
        This handler will send a message to a message queue
        with information about the lifecycle event.
        The mesage will only be sent if the settings.PUBLISH_LIFECYCLE 
        flag is set to True.
    '''
    
    host = settings.AMQP_HOST
    
    exchange_info = ('openethics_events', 'fanout')
    
    signal = kwargs['signal']
    
    if signal == application_created:
        event_type = 'created'
    elif signal == application_accepted_by_reviewer:
        event_type = 'accepted'
    elif signal == application_rejected_by_reviewer:
        event_type = 'rejected'
    else:
        raise AttributeError('An unkonwn signal triggered the receiver!')
    
    
    message = json.dumps({'application': kwargs['application'].id, 'event_type':event_type})
        
    if settings.PUBLISH_LIFECYCLE:   
        _send_message(host, exchange_info, message)
    
      
      
#connect to the signals of interest.  
application_created.connect(lifecycle_event_handler)
application_accepted_by_reviewer.connect(lifecycle_event_handler)
application_rejected_by_reviewer.connect(lifecycle_event_handler)