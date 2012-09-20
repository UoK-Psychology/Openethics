from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from questionnaire.models import Questionnaire
from django.core.exceptions import ImproperlyConfigured

class FinishedChecklistTestCase(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.ethicsApplication = EthicsApplication.objects.create(title='test application', principle_investigator=self.user)
        self.url = reverse('finished_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        
    def test_get_request_not_logged_in(self):
        '''
        If user is not logged in then they should get a page forbidden 403
        '''
        response = self.client.get(self.url)
        self.assertEquals (403, response.status_code )
        
    def test_get_invalid_application_id(self):
        '''
        If ethics applicatin ID is invalid we should get a 404 does not exist
        '''
        self.client.login(username='test', password='password') 
        url = reverse('finished_checklist', kwargs={'ethics_application_id':971234})
        response = self.client.get(url)
        self.assertEquals (404, response.status_code )
        
    def test_get_valid_firsttime(self):
        '''
        If ethics application model is valid and doesnt have an existing application 
        form questinnaire and user is logged in then:
            - a new application form questionnaire is created and associated to the 
            ethics application model
            - the application form questionnaire has the correct question groups
            configured based on settings.BASIC_APPLICATION_GROUPS
            - we should be redirected to the view page for the ethics application
        '''
        settings.BASIC_APPLICATION_GROUPS = [1,1,1]  # only group 1 is setup in the local fixture
        self.client.login(username='test', password='password') 
        response = self.client.get(self.url)
        
        self.ethicsApplication = EthicsApplication.objects.get(id=self.ethicsApplication.id)  #refresh our instance from the DB
        self.assertIsInstance(self.ethicsApplication.application_form, Questionnaire)
        
        applicationform_groups = [group.id for group in self.ethicsApplication.application_form.get_ordered_groups()]
        self.assertEqual(settings.BASIC_APPLICATION_GROUPS, applicationform_groups)    
        
        redirect_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})
        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver' + redirect_url)
        
    def test_get_valid_notfirsttime(self):
        '''
        If ethics application model is valid and does have an existing application 
        form questinnaire and user is logged in then:
            - check that the application form questionnaire doesn't change
            - we should be redirected to the view page for the ethics application
        '''
        settings.BASIC_APPLICATION_GROUPS = [1,1,1]
        self.client.login(username='test', password='password') 
        test_questionnaire=Questionnaire.objects.create(name='testname')
        self.ethicsApplication.application_form = test_questionnaire
        self.ethicsApplication.save() 
              
        response = self.client.get(self.url)
        #check that our EA has not been changed by getting it back from the DB and compairing it with
        #the one we created and stored away at the beginning
        self.ethicsApplication = EthicsApplication.objects.get(id=self.ethicsApplication.id)  #refresh our instance from the DB
        self.assertEqual(self.ethicsApplication.application_form, test_questionnaire)
        #check we got sent to the expected url
        redirect_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})

        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver' + redirect_url)

        
    def test_basic_application_group_setting_improperly_configured(self):
        '''
            If there is no settings.BASIC_APPLICATION_GROUPS or the groups it references 
            do not exist then an ImproperlyConfigured
            exception will be thrown
        '''
        if hasattr(settings, 'BASIC_APPLICATION_GROUPS'):
            del(settings.BASIC_APPLICATION_GROUPS)
        
        self.client.login(username='test', password='password') 
        self.assertRaises(ImproperlyConfigured, self.client.get, self.url)
        
        settings.BASIC_APPLICATION_GROUPS = [99999,]
        
        self.client.login(username='test', password='password') 
        self.assertRaises(ImproperlyConfigured, self.client.get, self.url)
        

