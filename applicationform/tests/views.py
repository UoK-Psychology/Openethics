from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from questionnaire.models import Questionnaire, QuestionGroup, AnswerSet
from django.core.exceptions import ImproperlyConfigured
from applicationform.views import _get_basic_application_groups,\
    _get_application_groups_from_checklist
from mock import patch


def _fabricate_checklist_questionnaire():
        
        questionnaire = Questionnaire.objects.create(name='checklist')
        questionnaire.add_question_group(QuestionGroup.objects.get(id=1))# questiongroup 1 should be configured as the checklist group by the intial data fixtures
        
        return questionnaire  
    
def _fabricate_checklist_answers_set(user, checklist):
    return AnswerSet.objects.create(user = user,
                             questionnaire=checklist,
                             questiongroup=checklist.get_ordered_groups()[0])
    
    
class FinishedChecklistTestCase(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.ethicsApplication = EthicsApplication.objects.create(title='test application', principle_investigator=self.user)
        
        
    def test_get_request_not_logged_in(self):
        '''
        If user is not logged in then they should get a page forbidden 403
        '''
        url = reverse('finished_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
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
        self.client.login(username='test', password='password') 
        url = reverse('finished_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        #no checklist configured
        response = self.client.get(url)
        self.assertEquals (404, response.status_code )
        
        #checklist configured bu is unanswered
        self.ethicsApplication.checklist = _fabricate_checklist_questionnaire()
        self.ethicsApplication.save()
        response = self.client.get(url)
        self.assertEquals (404, response.status_code )
        
    @patch('applicationform.views._get_application_groups_from_checklist')
    @patch('applicationform.views._get_basic_application_groups')
    def test_get_valid_firsttime(self, basic_function_mock, configure_function_mock):
        '''
            If this is the first time (i.e there is not an application already configured) then
            this function should call the _get_basic_application_groups and the _configure_application_form
            functions, concatenating the list of groups generated (basic application groups first) together.
            These groups should then be added to a new Questionnaire object which is assigned to the
            application_form field for the ethicsApplication.
            Once completed it should return to the view page for this ethics application
        '''
        
        #setup
        self.client.login(username='test', password='password') 
        url = reverse('finished_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        self.ethicsApplication.checklist = _fabricate_checklist_questionnaire()
        self.ethicsApplication.save()
        _fabricate_checklist_answers_set(self.user, self.ethicsApplication.checklist)
        
        basic_function_mock.return_value = [QuestionGroup.objects.get(id=2),QuestionGroup.objects.get(id=3)]
        configure_function_mock.return_value = [QuestionGroup.objects.get(id=4)]
        #test
        response = self.client.get(url)
        
        #confirm
        
        basic_function_mock.assert_called_once_with()
        configure_function_mock.assert_called_once_with(self.ethicsApplication)
        self.ethicsApplication = EthicsApplication.objects.get(id=self.ethicsApplication.id)#refresh instance!
        self.assertEqual(self.ethicsApplication.application_form.get_ordered_groups(), 
                         [QuestionGroup.objects.get(id=2),QuestionGroup.objects.get(id=3),QuestionGroup.objects.get(id=4)])
        
        redirect_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})

        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver' + redirect_url)
        
    def test_get_valid_notfirsttime(self):
        '''
            If there is already an ethicsApplication questionnaire, then this function should do nothing,
            and simply return to the view page for the ethics application.
        '''
        url = reverse('finished_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        self.client.login(username='test', password='password') 
        self.ethicsApplication.checklist = _fabricate_checklist_questionnaire()
        self.ethicsApplication.save()
        _fabricate_checklist_answers_set(self.user, self.ethicsApplication.checklist)
        test_questionnaire=Questionnaire.objects.create(name='testname')
        self.ethicsApplication.application_form = test_questionnaire
        self.ethicsApplication.save() 
              
        response = self.client.get(url)
        #check that our EA has not been changed by getting it back from the DB and compairing it with
        #the one we created and stored away at the beginning
        self.ethicsApplication = EthicsApplication.objects.get(id=self.ethicsApplication.id)  #refresh our instance from the DB
        self.assertEqual(self.ethicsApplication.application_form, test_questionnaire)
        #check we got sent to the expected url
        redirect_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})

        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver' + redirect_url)

        
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
    fixtures = ['get_application_groups_from_checklist.json']
    def setUp(self):
        self.user = User.objects.get(username='test_user')
     
       
    def test_checklist_incomplete(self):
        '''
            If the checklist for the ethiscApplication is incomplete, then this should thrown an 
            Attribute error, as the checklist answers are essential for this operation
        '''
        ethics_application = EthicsApplication.objects.create(title='test application', principle_investigator=self.user)
        #no checklist questionnaire
        self.assertRaises(AttributeError, _get_application_groups_from_checklist, ethics_application)  
        #checklist present but incomplete
        ethics_application.checklist = _fabricate_checklist_questionnaire()
        ethics_application.save()
        self.assertRaises(AttributeError, _get_application_groups_from_checklist, ethics_application) 
        
    def test_checklist_complete(self):
        '''
            If the checklist is complete then this function should locate all the questions
            that responded True, then do a look up to get a list of all the QuestionGroups that are linked
            to this question.
            The function should then create a QuestionGroup set, which will exclude duplicates of groups that are
            linked to more than one question, only adding them the first time they are included by a question.
            
            this test makes use of the above fixture
            checklist question 2 links to groups 6 and 7
            checklist question 3 links to groups 7
            checklist question 4 links to groups 8
            
            there is an answerset for the checklist in ethics application 1, and questions 2,3,4 have been
            answered as yes
            
            therefore we should expect to get a groups 6,7,8 back in that order, importantly we shouldn't
            see 6,7,7,8 returned
        '''
    
        test_application = EthicsApplication.objects.get(id=1)
        returned_groups = _get_application_groups_from_checklist(test_application)
        self.assertEqual(returned_groups,
                         [
                          QuestionGroup.objects.get(id=6),
                          QuestionGroup.objects.get(id=7),
                          QuestionGroup.objects.get(id=8),
                          ])
        
        

