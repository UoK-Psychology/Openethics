from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mock import patch, call
from ethicsapplication.models import EthicsApplication
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
            active_applications : applications that the user is the pi for an are in the state *with reviewer*
            applications_in_review: applications that the user is the pi for and are in the state *awaiting_approval*
            approved_applications: applications that the user is the pi for and are in the state *approved*
            
            these lists are generated using the get_applications_for_principle_investigator function
            passing in the specific state filter. This function is mocked in this test.
        '''
        
        '''
            Below we do a mock up for get_active_applications() and hardwire for it to return what we expect before each call.
            This means it can run as a unit test in isolation of EthicsApplicationManager
        '''
        with patch('ethicsapplication.models.EthicsApplicationManager.get_applications_for_principle_investigator') as manager_mock:
            
           
            
            manager_mock.return_value = []     #set what value we want the call the get_active_applicaitons() to return below..
            
            #have a user, and be logged in
            #get request to the index page
            self.client.login(username='test', password='testpass')   
            response = self.client.get(reverse('index_view'))   #the context returned by a call to index_view will include the result
                                                                #of a call to get_active_applications.
            
            #assert 200
            #assert the template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                'index.html')
            #assert context
            
            self.assertEqual(response.context['active_applications'], [])
            self.assertEqual(response.context['applications_in_review'], [])
            self.assertEqual(response.context['approved_applications'], [])
            
            #assert that manager_mock is called
            self.assertTrue(call(self.user, 'with_researcher') in manager_mock.mock_calls)
            self.assertTrue(call(self.user, 'awaiting_approval') in manager_mock.mock_calls)
            self.assertTrue(call(self.user, 'approved') in manager_mock.mock_calls)

        
    def test_user_is_logged_in_has_applications_for_review(self):
        '''
            If the user has got applications that they are the reviewer for, which are in the state
            '*awaiting approval* then they should
            be listed in the context as applications_for_review
        '''
        with patch('ethicsapplication.models.EthicsApplicationManager.get_applications_for_reviewer') as manager_mock:
            
            application_for_review = EthicsApplication.objects.create(title='test', principle_investigator=self.user)
            manager_mock.return_value = [application_for_review]      #set what value we want the call the get_active_applicaitons() to return below..
            
            #have a user, and be logged in
            #get request to the index page
            self.client.login(username='test', password='testpass')   
            response = self.client.get(reverse('index_view'))   #the context returned by a call to index_view will include the result
                                                                #of a call to get_active_applications.
            
            #assert 200
            #assert the template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                'index.html')
            #assert context
            self.assertTrue('applications_for_review' in response.context)
            self.assertEqual(response.context['applications_for_review'], [application_for_review] )
            #assert that manager_mock is called
            manager_mock.assert_called_with(self.user, 'awaiting_approval')

    