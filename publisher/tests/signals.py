from django.test import TestCase


class SignalsTests(TestCase):
    
    def test_signal_bindings(self):
        '''
            This module should be connected to the following signal:
            
            application_created
            application_accepted_by_reviewer
            application_rejected_by_reviewer
    
            when any of these signals is raised then the lifecycle_event_handler should be called
        '''
        
        self.assertTrue(False)
        
    def test_event_handler(self):
        '''
            When the event handler is called , it should connect to an AMQP server
            using the connection details from the settings file (AMQP_SERVER).
            
            It should then connect to a fanout exchange called 'openethics_events'.
            
            Finally it should publish a message to this exchange, the contents of this message
            should be a JSON string:
            {'event_type':<application_created|application_accepted_by_reviewer|application_rejected_by_reviewer>,
                'application':<application_id>}
        '''
        self.assertTrue(False)