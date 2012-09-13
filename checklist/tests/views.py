from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from questionnaire.models import QuestionGroup, Questionnaire
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ethicsapplication.models import EthicsApplication



class StartChecklistTestCase(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.ethicsApplication = EthicsApplication.objects.create(title='test application', principle_investigator=self.user)
        
        
    def test_start_checklist_logged_in_checlist_configured_firsttime(self):
        '''
            A GET request to the do_checklist url, passing in an id for an ehticsapplication
            should check to se if there is an questionnaire associated to this ethicsapplication
            if there isn't then it should create one, using the group defined in Settings.CHECKLIST_ID
            to set the one and only group.
            It should then redirect to the do_questionnaire url passing the newly created questionnaire id 
            in as the questionnaire_id argument, and the url for the application_view for this application
            in as the on_success get parameter (so that you return to the applicaton view when you finish the 
            checklist)
            
            variants:
            ethics application already has a checklist questionnaire
        '''
        settings.CHECKLIST_ID = 1
        self.client.login(username='test', password='password') 
        url = reverse('start_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
        
        #get the latest questionnaire
        new_questionnaire = Questionnaire.objects.latest('id')
        self.assertEqual(new_questionnaire.get_ordered_groups()[0].id, int(settings.CHECKLIST_ID))
        self.assertEqual(new_questionnaire.checklist_questionnaire.get(), self.ethicsApplication)
        
        base_url = reverse('do_checklist', kwargs={'questionnaire_id':new_questionnaire.id})
        on_success_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})
        url = '%s?on_success=%s' % (base_url, on_success_url)
        
        self.assertRedirects(response, expected_url=url)
        
    def test_start_checklist_logged_in_checlist_configured_nexttime(self):   
        '''
            If there is already a questionnaire assoicated with the ethics application, then no more questionnaires should
            be made, and instead you should be redirected straight to the the do_checklist url with that questionnaire_id
        '''
        self.client.login(username='test', password='password') 
        settings.CHECKLIST_ID = 1
        
        #setup
        test_questionnaire = Questionnaire.objects.create(name='my_test_questionnaire')
        test_questionnaire.add_question_group(QuestionGroup.objects.get(pk=settings.CHECKLIST_ID))
        self.ethicsApplication.checklist = test_questionnaire
        self.ethicsApplication.save()
        
        questionnaire_count = len(Questionnaire.objects.all())
        
        url = reverse('start_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
        
        base_url = reverse('do_checklist', kwargs={'questionnaire_id':test_questionnaire.id})
        on_success_url = reverse('application_view', kwargs={'application_id':self.ethicsApplication.id})
        url = '%s?on_success=%s' % (base_url, on_success_url)
        
        self.assertRedirects(response, expected_url=url)
        self.assertEqual(questionnaire_count, len(Questionnaire.objects.all()))

    def test_start_checklist_not_logged_in(self):
        '''
            If the user is not logged in then they should get redirected to the login page
        '''
        url = reverse('start_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % url )
        
    def test_start_checklist_invalid_ethicsapplication(self):
        '''
            If the ethics application_id does not exist in the database then should throw a http 404 error code
        '''
        self.client.login(username='test', password='password') 
        response = self.client.get(reverse('start_checklist', kwargs={'ethics_application_id':5000000}))
        self.assertEqual(response.status_code, 404)
        
    def test_start_checlkist_setting_not_configured(self):
        '''
            If the settings.CHECKLIST_ID is not present then an ImproperlyConfigured exception will
            be raised
        '''
        if hasattr(settings, 'CHECKLIST_ID'):
            del(settings.CHECKLIST_ID)
            
        self.client.login(username='test', password='password') 
        self.assertRaises(ImproperlyConfigured, self.client.get, reverse('start_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id}))
        
    def test_start_checklist_setting_improperly_configured(self):
        '''
            If there is no questiongroup with a id of settings.CHECKLIST_ID then an ImproperlyConfigured
            exception will be thrown
        '''
        settings.CHECKLIST_ID = 500
        self.client.login(username='test', password='password') 
        self.assertRaises(ImproperlyConfigured, self.client.get,reverse('start_checklist', kwargs={'ethics_application_id':self.ethicsApplication.id}))

                
        
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
        
        