from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from questionnaire.models import Questionnaire, QuestionGroup, AnswerSet,\
    QuestionAnswer
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
        url = reverse('configure_application_form', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
        self.assertEquals (403, response.status_code )
        
    def test_get_invalid_application_id(self):
        '''
        If ethics applicatin ID is invalid we should get a 404 does not exist
        '''
        self.client.login(username='test', password='password') 
        url = reverse('configure_application_form', kwargs={'ethics_application_id':971234})
        response = self.client.get(url)
        self.assertEquals (404, response.status_code )
    
    
          
    def test_checklist_not_complete(self):
        '''
            If the checklist is not completed for the ethics application supplied, then a 404 error
            should be thrown
        '''
        self.client.login(username='test', password='password') 
        url = reverse('configure_application_form', kwargs={'ethics_application_id':self.ethicsApplication.id})
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
        url = reverse('configure_application_form', kwargs={'ethics_application_id':self.ethicsApplication.id})
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
        url = reverse('configure_application_form', kwargs={'ethics_application_id':self.ethicsApplication.id})
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
            checklist question 1 links to group 9
            checklist question 2 links to groups 6 and 7
            checklist question 3 links to groups 7
            checklist question 4 links to groups 8
            
            there is an answerset for the checklist in ethics application 1, and questions 2,3,4 have been
            answered as yes
            
            therefore we should expect to get a groups 6,7,8 back in that order, importantly we shouldn't
            see 6,7,7,8 returned, nor 9 returned as this question is answered as no.
        '''
    
        test_application = EthicsApplication.objects.get(id=1)
        returned_groups = _get_application_groups_from_checklist(test_application)
        self.assertEqual(returned_groups,
                         [
                          QuestionGroup.objects.get(id=6),
                          QuestionGroup.objects.get(id=7),
                          QuestionGroup.objects.get(id=8),
                          ])
        
class ViewApplicationSectionTests(TestCase):
    
    def setUp(self):
        '''
            Sets up the shared pre-requisites for the tests.
        '''
        self.testUser = User.objects.create_user('test', 'test@home.com', "password")
        self.test_application = EthicsApplication.objects.create(principle_investigator=self.testUser,
                                                                 title='test application')
        self.test_questionnaire = Questionnaire.objects.create(name='test questionnaire')
        self.test_group = QuestionGroup.objects.create(name='test group')
        self.test_questionnaire.add_question_group(self.test_group)
        self.valid_url = reverse('view_application_form_group', kwargs={'ethics_application_id':self.test_application.id,
                                                             'questionnaire_id':self.test_questionnaire.id,
                                                             'order_index':0})
        
        
    def test_authentication(self):
        '''
            The user must be loggin in to access this view, if they
            aren't then they should be redirected to login
        '''        
        
        response = self.client.get(self.valid_url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.valid_url )
        
    def test_invalid_parameters(self):
        '''
            If the questionniare or the ethics application is not present then 
            the requester should get a 404 response.
            If the order_index is invalid - i.e. there is no group available at that
            index in the questionnaire the user should get a 404 error
        '''
        self.client.login(username='test', password='password')
        invalid_application_url = reverse('view_application_form_group', kwargs={'ethics_application_id':999,
                                                             'questionnaire_id':self.test_questionnaire.id,
                                                             'order_index':0})
        
        invalid_questionnaire_url = reverse('view_application_form_group', kwargs={'ethics_application_id':self.test_application.id,
                                                             'questionnaire_id':999,
                                                             'order_index':0})
        
        invalid_group_url = reverse('view_application_form_group', kwargs={'ethics_application_id':self.test_application.id,
                                                             'questionnaire_id':self.test_questionnaire.id,
                                                             'order_index':999})
        
        for url in [invalid_application_url,invalid_questionnaire_url,invalid_group_url]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            
        
    @patch('applicationform.views.has_permission')  
    def test_authorization(self, has_permission_mock):
        '''
            The user must have the view permission for the ethics application
            in question. If they don't then they should get a 403 forbidden error
        '''
        self.client.login(username='test', password='password')  
        has_permission_mock.return_value = False
        
        response = self.client.get(self.valid_url)
        self.assertEquals (403, response.status_code )
        
    
    def carryout_shared_assertions(self, expected_question_answers):
        '''
            This function is shared between the test_no_answerset and
            test_answerset_avaialble tests as only their setup differs
            
            It asserts that
            The Get request returns 200
            the template that is used is : applicationform/read_application_form.html
            the context contains a key : return_to which is the same as the return_to arg sent in the get request
            the context also contains a key: question_Answers which should match the expected_question_answers parameter
        '''
        with patch('applicationform.views.has_permission') as has_permission_mock:
            has_permission_mock.return_value = True
            self.client.login(username='test', password='password') 
            return_to_url = 'a_url'
            
            self.client.login(username='test', password='password') 
            
            response = self.client.get(self.valid_url,{'return_to':return_to_url})
            
            
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                    'applicationform/read_application_form.html')
            self.assertTrue('return_to' in response.context)
            self.assertTrue('question_Answers' in response.context)
            
            self.assertEqual(response.context['return_to'], return_to_url)
            self.assertEqual(response.context['question_Answers'], expected_question_answers)   
            
    @patch('applicationform.views.has_permission')      
    def test_answerset_avaialble(self, has_permission_mock):
        '''
            If everything goes well:
            1. If there is no answerset available then then there should be an empty
            list keyed against question_answers in the context.
            2. If there is an answerset then the get_latest_question_Answer_in_order function
            on the answerset should be called, and it should put the returned list in the context, keyed
            with "question_answers"
        '''
        #first, when there is no answerset present:
        self.carryout_shared_assertions([])
        
        #now setup the answerset
        AnswerSet.objects.create(   user=self.testUser,
                                    questionnaire=self.test_questionnaire,
                                    questiongroup=self.test_group)
        
        with patch('questionnaire.models.AnswserSet.get_latest_question_answer_in_order') as answer_set_mock:
            answer_set_mock.return_value = [QuestionAnswer()]
            self.carryout_shared_assertions(answer_set_mock.return_value)

        
