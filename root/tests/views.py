from django.test import TestCase
from mock import patch



class IndexViewTestCase(TestCase):
    
    
    def test_user_not_logged_in(self):
        '''
            If a non logged in user does a get request to the index url
            they should sent directly to the index page
        '''
        self.assertTrue(False, 'Not implemented yet')
        
    def test_user_is_logged_in_has_active_applications(self):
        '''
            If a user is logged in then the context should include:
            active_applications : which is a list of application objects which in this test should be empty
            this should be fetched using a call to the get_active_applications manager function 
            which is mocked in this test
        '''
        
        
        with patch('ethicsapplication.models.EthicsApplicationManager') as manager_mock:
            manager_mock.return_value = [1,2,3]
            
            
        self.assertTrue(False, 'Not implemented yet')

