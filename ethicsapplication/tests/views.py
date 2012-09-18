'''
This will test all the view code for the ethicsapplication application

Created on Jul 25, 2012
@author: jasonmarshall
'''


from django.test import TestCase
from django.core.urlresolvers import reverse
from ethicsapplication.forms import EthicsApplicationForm
from django.contrib.auth.models import User
from ethicsapplication.models import EthicsApplication
from django.conf import settings

class CreateViewsTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@home.com', 'testpass')
        self.user.save()
        settings.APPLICATION_WORKFLOW = 'Ethics_Application_Approval'
        
    
    def test_create_Application_not_logged_in(self):
        '''
            If there is no user logged in, you should be redirected to the login url
        '''
        response = self.client.get(reverse('create_application_view'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('create_application_view') )
        
    def test_create_application_get(self):
        '''
            A GET request to the create_application_view url should if the user logged in:
            
            1. Return a http 200 status code.
            2. Use the template ethicsapplication/create.html.
            3. Have a form object in the context.
        '''
        self.client.login(username='test', password='testpass')   
        response = self.client.get(reverse('create_application_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'ethicsapplication/create.html')
        self.failUnless(isinstance(response.context['form'],
                                   EthicsApplicationForm))
        
    def test_create_application_valid_post(self):
        '''
            A valid post to this view, for a user that is logged in
            should consist of:
            1. a title
            
            and should:
            1. Create a new Ethics Application in the databse
            2. return http 302 (redirect)
            3. should redirect to the view application page for the new application
            4. The PI for the newly created EthicsApplication should be the user that was logged in.
        '''
        post_data = {'title':'test application'}
        self.client.login(username='test', password='testpass')   
        response = self.client.post(reverse('create_application_view'),post_data)
        applications = EthicsApplication.objects.all()
        
        self.assertTrue(len(applications) ==1)
        the_application = EthicsApplication.objects.get(pk=1)
        self.assertEqual(the_application.title, 'test application')
        self.assertEqual(the_application.principle_investigator, self.user)
        self.assertRedirects(response, reverse('application_view', kwargs={'application_id':applications[0].id}))
        
        
    def test_create_application_invalid_post(self):
        '''
            An invalid post to this view, for a user that is logged in
            should consist of:
            1. no title
            
            and should:
            1. not create a new Ethics Application in the databse
            2. render the form bound to the previous answers
            3. have an error in the form for not supplying a title
        '''
        
        post_data = {}
        self.client.login(username='test', password='testpass')   
        response = self.client.post(reverse('create_application_view'),post_data)
        applications = EthicsApplication.objects.all()
        
        self.assertTrue(len(applications) ==0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'ethicsapplication/create.html')
        self.failUnless(isinstance(response.context['form'],
                                   EthicsApplicationForm))
        
        self.assertEquals(response.context['form']['title'].errors[0], 'This field is required.')


class ViewApplictionTestCase(TestCase):
    '''
        Test case to test the view ethics applications functions
        Inlcudes a test fixture called 'ethics_application_tests_fixture.json which
        defines two users and two test ethics application one registered to each user
    '''
    fixtures = ['ethics_application_tests_fixture.json']
    
    
        
      
    def test_valid_application_id_no_user(self):
        '''
            You must be logged in to use this view, if you aren't then you should be redirected to the
            login page
        '''
        
        url = reverse('application_view', kwargs={'application_id':1})
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % url )
        
    def test_invalid_application_id(self):
        '''
            If the object does not exist you should get a 404 response
        '''
        
        self.client.login(username='test_user_1', password='password')   
        response = self.client.get(reverse('application_view', kwargs={'application_id':10}))
        self.assertEqual(response.status_code, 404)
        
    def test_valid_application_user_no_view_permission(self):
        '''
            You must be logged in and have the 'view' permission for the application that you are trying to view
            if you don't have permission you will get a 403 error
        '''
        self.client.login(username='test_user_1', password='password')   
        response = self.client.get(reverse('application_view', kwargs={'application_id':2}))
        self.assertEqual(response.status_code, 403)
        
    def test_valid_application_user_with_view_permission(self):
        '''
            You must be logged in and have the 'view' permission for the application that you are trying to view.
            With the correct user logged in you should:
            1. get 200 http response
            2. the remplate should be "ethicsapplication/view_ethics_application.html'
            3. the context should contain a field called application containing the EthicsApplication object.
        '''
        
        self.client.login(username='test_user_2', password='password')   
        response = self.client.get(reverse('application_view', kwargs={'application_id':1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('ethicsapplication/view_ethics_application.html') 
        self.assertTrue('application' in response.context)
        self.assertIsInstance(response.context['application'], EthicsApplication)
        
class SetChecklistContextTestCase(TestCase):
    
    
    def test_checklist_questionnaire_not_set(self):
        '''
            If there has not been a checklist setup yet (i.e. the checklist has not been
            started) then this function shouldn't do anything 
        '''
        self.assertTrue(False)
        
    def test_no_answer_set_for_application(self):
        '''
            If there is no answerset for the ethics application checklist
            then this function should do nothing
        '''
        self.assertTrue(False)
        
        
    def test_checklist_and_answerset_available(self):
        '''
            If there is both a checklist questiongroup, and there is an answerset for it, based
            on the user and the questionnaire then this function should set the context on the checklist
            group using the answerset
        '''
        self.assertTrue(False)
    