from django.test import TestCase
from mock import patch, call
from ethicsapplication.signals import application_created
from review.signals import application_accepted_by_reviewer,\
    application_rejected_by_reviewer
from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.conf import settings
import json
from publisher.signals import lifecycle_event_handler

class SignalsTests(TestCase):
    
    def test_signal_bindings(self):
        '''
            This module should be connected to the following signal:
            
            application_created
            application_accepted_by_reviewer
            application_rejected_by_reviewer
    
            when any of these signals is raised then the lifecycle_event_handler should be called
        '''
        signals_to_test = [application_created, application_accepted_by_reviewer, application_rejected_by_reviewer]
        
        #check that  our function is in the registered functions for each of the required signals
        for signal in signals_to_test:
            registered_functions = [r[1]() for r in signal.receivers]
            self.assertTrue(lifecycle_event_handler in registered_functions)
        
    def test_event_handler(self):
        '''
            When the event handler is called , it should call the _send_message
            function using the connection details from the settings file (AMQP_HOST),
            specifying a fanout exchange called 'openethics_events' and a message which is a
            JSON string like=:
            {'event_type':<application_created|application_accepted_by_reviewer|application_rejected_by_reviewer>,
                'application':<application_id>}
                
            the event_type will depend on the signal that triggered the receiver.
        '''
        
        
        test_application = EthicsApplication.objects.create(title='test application', 
                                                            principle_investigator=User.objects.create_user('username', 'email', 'password'))
        test_params = [(application_created, 'created'), (application_accepted_by_reviewer, 'accepted'), (application_rejected_by_reviewer, 'rejected')]
        
        #now that we have created our test ethics application it is safe to turn on the Publish_lifecycle flag
        settings.PUBLISH_LIFECYCLE = True
        
        with patch('publisher.signals._send_message') as send_message_mock:
            for param in test_params:
                lifecycle_event_handler(None, signal=param[0], application=test_application)
                
        self.assertEqual(send_message_mock.mock_calls, [
            call('localhost', ('openethics_events', 'fanout'), '{"application": 1, "event_type": "created"}'),
            call('localhost', ('openethics_events', 'fanout'), '{"application": 1, "event_type": "accepted"}'),
            call('localhost', ('openethics_events', 'fanout'), '{"application": 1, "event_type": "rejected"}')
                                                        ])
        
        settings.PUBLISH_LIFECYCLE = False
        
        
            