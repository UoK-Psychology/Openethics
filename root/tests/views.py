from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mock import patch
class IndexViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@home.com', 'testpass')
        self.user.save()
        
    def test_user_not_logged_in(self):
        '''
            If a non logged in user does a get request to the index url
            they should sent directly to the index page
        '''
        response = self.client.get(reverse('index_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                            'index.html')
        #assert context
        self.assertFalse('active_applications' in response.context)
        
    def test_user_is_logged_in_has_active_applications(self):
        '''
            If a user is logged in then the context should include:
            active_applications : which is a list of application objects which in this test should be empty
            this should be fetched using a call to the get_active_applications manager function 
            which is mocked in this test
        '''
        
        
        with patch('ethicsapplication.models.EthicsApplicationManager.get_active_applications') as manager_mock:
            
           
            manager_mock.return_value = []
            
            #have a user, and be logged in
            #get request to the index page
            self.client.login(username='test', password='testpass')   
            response = self.client.get(reverse('index_view'))
            
            #assert 200
            #assert the template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                'index.html')
            #assert context
            self.assertTrue('active_applications' in response.context)
            self.assertEqual(response.context['active_applications'], [])
            #assert that manager_mock is called
            manager_mock.assert_called_with(self.user)

