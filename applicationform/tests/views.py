from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from questionnaire.models import Questionnaire, QuestionGroup
from django.core.exceptions import ImproperlyConfigured
from applicationform.views import _get_basic_application_groups

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
        
    def test_checklist_not_complete(self):
        '''
            If the checklist is not completed for the ethics application supplied, then a 404 error
            should be thrown
        '''
        self.assertTrue(False)
        
    def test_get_valid_firsttime(self):
        '''
            If this is the first time (i.e there is not an application already configured) then
            this function should call the _get_basic_application_groups and the _configure_application_form
            functions, concatenating the list of groups generated (basic application groups first) together.
            These groups should then be added to a new Questionnaire object which is assigned to the
            application_form field for the ethicsApplication.
            Once completed it should return to the view page for this ethics application
        '''
        self.assertTrue(False)
        
    def test_get_valid_notfirsttime(self):
        '''
            If there is already an ethicsApplication questionnaire, then this function should do nothing,
            and simply return to the view page for the ethics application.
        '''
        self.assertTrue(False)
        
class GetBasicApplicationGroupsTests(TestCase):
    
    def setUp(self):
        settings.BASIC_APPLICATION_GROUPS = []
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.ethicsApplication = EthicsApplication.objects.create(title='test application', principle_investigator=self.user)
       
    def test_valid_configuration(self):
        '''
            If the configuration of the basic application groups is valid then this function should
            return a list of Questiongroups representing the configured id's, in the same order as is specified
            in the setting
        '''
        settings.BASIC_APPLICATION_GROUPS = [1,3,2]  # only group 1 is setup in the initial_data fixture
       
        groups = _get_basic_application_groups()
        self.assertEqual(groups,
                         [
                              QuestionGroup.objects.get(id=settings.BASIC_APPLICATION_GROUPS[0]),
                              QuestionGroup.objects.get(id=settings.BASIC_APPLICATION_GROUPS[1]),
                              QuestionGroup.objects.get(id=settings.BASIC_APPLICATION_GROUPS[2]),
                          ])
        
    def test_setting_improperly_configured(self):
        '''
            If there is no settings.BASIC_APPLICATION_GROUPS or the groups it references 
            do not exist then an ImproperlyConfigured
            exception will be thrown
        '''
        
        del(settings.BASIC_APPLICATION_GROUPS)#setting not present
        
        self.assertRaises(ImproperlyConfigured, _get_basic_application_groups)
        
        settings.BASIC_APPLICATION_GROUPS = [99999,]#groups don't exist for setting
        
        self.assertRaises(ImproperlyConfigured, _get_basic_application_groups)
        
        
class GetApplicationGroupsFromChecklistTests(TestCase):
    def test_checklist_incomplete(self):
        '''
            If the checklist for the ethiscApplication is incomplete, then this should thrown an 
            Attribute error, as the checklist answers are essential for this operation
        '''
        self.assertTrue(False)  
        
    def test_checklist_complete(self):
        '''
            If the checklist is complete then this function should locate all the questions
            that responded True, then do a look up to get a list of all the QuestionGroups that are linked
            to this question.
            The function should then create a QuestionGroup set, which will exclude duplicates of groups that are
            linked to more than one question, only adding them the first time they are included by a question.
        '''
        self.assertTrue(False)     
        

