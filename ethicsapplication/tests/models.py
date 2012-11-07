from django.test import TestCase
from ethicsapplication.models import EthicsApplication, EthicsApplicationManager
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.conf import settings
from mock import patch, MagicMock, call
from django.core.exceptions import ImproperlyConfigured
from workflows.models import Workflow, State
from questionnaire.models import Questionnaire, QuestionGroup, AnswerSet
from permissions.models import Role
class EthicsApplicationModelTestCase(TestCase):
    
    def setUp(self):
        settings.APPLICATION_WORKFLOW = 'Ethics_Application_Approval'
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'Principle_Investigator'
        settings.REVIEWER_ROLE = 'Reviewer'
        
        self.test_user = User.objects.create_user('test', 'me@home.com', 'password')
        self.ethics_application = EthicsApplication.objects.create(title='test_application', 
                                                                   principle_investigator=self.test_user)
    
    def test_valid_EthicsApplication_creation(self):
        '''
            You should be able to create a valid EthicsApplication
            with:
            1. Title (less than 255 characters)
            2. Principle Investigator
            3. No application
            
            The active flag should default to True
        
        '''
        
        a_user = self.test_user
        ethicsApplication = EthicsApplication(title='test application', principle_investigator=a_user)
        ethicsApplication.save()
        
        self.assertTrue(ethicsApplication.title == 'test application')
        self.assertTrue(ethicsApplication.principle_investigator == a_user)
        self.assertTrue(ethicsApplication.application_form == None)
        self.assertTrue(ethicsApplication.active)

    def test_invalid_EthicsApplication_creation_no_pi(self):
        '''
            If you don't supply a principle investigator then you will get an exception
        '''
        ethicsApplication = EthicsApplication(title='test application')

        self.assertRaises(IntegrityError, ethicsApplication.save)

    def test_invalid_EthicsApplication_creation_no_title(self):
        '''
            If you don't supply a title then you will get an exception
        '''
        a_user = self.test_user
        ethicsApplication = EthicsApplication( principle_investigator=a_user)
        
        self.assertRaises(IntegrityError, ethicsApplication.save)

    def test_ethicsapplication_manager(self):
        
        '''
            The default manager for an ethicsapplication should be an instance of EthicsApplicationManager
            which is a custom manager that adds some table level functionality.
        '''
        self.assertIsInstance(EthicsApplication.objects, EthicsApplicationManager)  
     
    @patch('ethicsapplication.models.EthicsApplication._add_to_workflow') 
    def test_workflow_add_on_new_ethicsapplications(self, patched_function):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow using the _add_to_workflow function, if it is an existing entity then
            the _add_to_wokrflow function should not be called
        
        ''' 

            
        #create a new ethicsapplication object and save it
        a_user = self.test_user
        my_Application = EthicsApplication(title='test', principle_investigator=a_user)
        my_Application.save()
        #assert that it was called once
        patched_function.assert_called_once_with()
        
        #make a change and save, the patch should not be called again!
        my_Application.title = 'changed'
        my_Application.save()
        
        patched_function.assert_called_once_with()
        
        
    def test_add_to_workflow_setting_absent(self):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow defined in the settings.APPLICATION_WORKFLOW setting. In this case
            the setting is not present so an ImproperlyConfigured exception is raised
        
        ''' 
        settings.APPLICATION_WORKFLOW = None
        test_application = EthicsApplication(title='test', principle_investigator=self.test_user)
        self.assertRaises(ImproperlyConfigured, test_application._add_to_workflow)
        
    def test_add_to_workflow_setting_invalid(self):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow defined in the settings.APPLICATION_WORKFLOW setting. In this case
            the setting is present but the workflow doesn't exist in the db so an ImproperlyConfigured
            exception is raised.
        
        ''' 
        
        settings.APPLICATION_WORKFLOW = 'Does not exist!'
        test_application = EthicsApplication(title='test', principle_investigator=self.test_user)
        self.assertRaises(ImproperlyConfigured, test_application._add_to_workflow)
    
    @patch('ethicsapplication.models.set_workflow')#patched in the model module as this is the namespace it will be used from
    def test_add_to_workflow_setting_valid(self, set_workflow_mock):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow defined in the settings.APPLICATION_WORKFLOW setting. In this case
            the setting is present and the workflow has been configured in the db,
            so no exception should be run and a call should be made to the 
            set_workflow function.
        
        ''' 
        
        approval_workflow = Workflow.objects.get(name='Ethics_Application_Approval')
        settings.APPLICATION_WORKFLOW = 'Ethics_Application_Approval'
        test_application = EthicsApplication(title='test', principle_investigator=self.test_user)
        test_application.save()
        set_workflow_mock.assert_called_once_with(test_application, approval_workflow)
     
     
    @patch('ethicsapplication.models.EthicsApplication._add_to_principle_investigator_role')    
    def test_update_principle_investigator(self, function_mock):
        '''
            When the save method is called, if the principle investigator property has been changed then
            _add_to_principle_investigator_role function should be called to update the 
            membership of this group
        '''
        test_application = EthicsApplication(title='test', principle_investigator=self.test_user)
        test_application.save()
        
        self.assertEqual(function_mock.call_count , 1)
        
        test_application.principle_investigator = User.objects.create_user('test2', 'me2@home.com', 'password2')
        test_application.save()
        
        self.assertEqual(function_mock.call_count , 2)
        
        test_application.active = False
        test_application.save()
        
        self.assertEqual(function_mock.call_count , 2)
    
    def test_absent_PI_role_in_settings(self):
        '''
            test that if there settings.PRINCIPLE_INVESTIGATOR_ROLE is not present
            or doesn't exist in the db then a ImproperlyCOnfigured exception should be raised.
        '''
        settings.PRINCIPLE_INVESTIGATOR_ROLE = None
        
        self.assertRaises(ImproperlyConfigured, self.ethics_application._add_to_principle_investigator_role)
        
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'Does Not exist'
        self.assertRaises(ImproperlyConfigured, self.ethics_application._add_to_principle_investigator_role)
        
   
    @patch('ethicsapplication.models.Role')
    @patch('ethicsapplication.models.add_local_role') 
    @patch('ethicsapplication.models.remove_local_role') 
    def test_add_to_principle_investigator_role_no_existing_user(self, remove_local_role_mock, 
                                                              add_local_role_mock, role_mock):
        '''
            If the current user in the PI role is the same as the existing one then nothing should 
            happen.
        '''
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'Principle_Investigator'
        
        a_role_mock = MagicMock(name='a_role')
        a_role_mock.get_local_users.return_value = []
        
        role_mock.objects.get.return_value =  a_role_mock
        user1 = self.test_user
        
        test_application = EthicsApplication(title = 'test', principle_investigator=user1)
        
        test_application._add_to_principle_investigator_role()
        
        a_role_mock.get_local_users.assert_called_once_with(test_application)
        self.assertEqual(0, remove_local_role_mock.call_count)
        self.assertEqual([call(test_application, user1, a_role_mock)], add_local_role_mock.mock_calls)
        
    @patch('ethicsapplication.models.Role')
    @patch('ethicsapplication.models.add_local_role') 
    @patch('ethicsapplication.models.remove_local_role') 
    def test_add_to_principle_investigator_role_existing_different_user(self, remove_local_role_mock, 
                                                              add_local_role_mock, role_mock):
        '''
            If the current user in the PI role is the same as the existing one then nothing should 
            happen.
        '''
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'Principle_Investigator'
        
        user1 = self.test_user
        user2 = User.objects.create_user('test2', 'me2@home.com', 'password2')
        
        a_role_mock = MagicMock(name='a_role')
        a_role_mock.get_local_users.return_value = [user2]
        role_mock.objects.get.return_value =  a_role_mock
        
        test_application = EthicsApplication(title = 'test', principle_investigator=user1)
        
        test_application._add_to_principle_investigator_role()
        
        a_role_mock.get_local_users.assert_called_once_with(test_application)
        remove_local_role_mock.assert_called_once_with(test_application, user2, a_role_mock)
        add_local_role_mock.assert_called_once_with(test_application, user1, a_role_mock)
        
    @patch('ethicsapplication.models.Role')
    @patch('ethicsapplication.models.add_local_role') 
    @patch('ethicsapplication.models.remove_local_role') 
    def test_add_to_principle_investigator_role_existing_same_user(self, remove_local_role_mock, 
                                                              add_local_role_mock, role_mock):
        '''
            If the current user in the PI role is the same as the existing one then nothing should 
            happen.
        '''
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'Principle_Investigator'
        
        user1 = self.test_user
        
        
        a_role_mock = MagicMock(name='a_role')
        a_role_mock.get_local_users.return_value = [user1]
        role_mock.objects.get.return_value =  a_role_mock
        
        test_application = EthicsApplication(title = 'test', principle_investigator=user1)
        
        test_application._add_to_principle_investigator_role()
        
        a_role_mock.get_local_users.assert_called_once_with(test_application)
        self.assertEqual(remove_local_role_mock.call_count, 0)
        self.assertEqual(add_local_role_mock.call_count, 0)
        
    
    def _fabricate_empty_questionnaire(self, name):
        test_questionnaire = Questionnaire.objects.create(name=name)
        test_group = QuestionGroup.objects.create(name=name)
        test_questionnaire.add_question_group(test_group)
        return test_questionnaire
        
    def _fabricate_checklist(self, ethics_application):
        ethics_application.checklist = self._fabricate_empty_questionnaire('checklist')
    def _fabricate_application_form(self, ethics_application):
        ethics_application.application_form = self._fabricate_empty_questionnaire('application')
        
    def _fabricate_answerset(self, user, questionnaire):
        return  AnswerSet.objects.create(user=user,
                                         questionnaire=questionnaire,
                                         questiongroup=questionnaire.get_ordered_groups()[0])

    def test_get_answersets_for_questionnaire_none(self):
        '''
            If you pass None into this function then it will return an empty list
        '''
        self.assertEqual(self.ethics_application._get_answersets_for_questionnaire(None), {})
    
    def test_get_answersets_for_questionnaire_no_groups(self):
        '''
            If you pass a questionnaire that has no groups into this function then it will return an empty list
        '''
        self.assertEqual(self.ethics_application._get_answersets_for_questionnaire(Questionnaire.objects.create(name='test')), {})
            
    def test__get_answersets_for_questionnaire_groups_no_data(self):
        '''
            If a group doesn't have an answerset then it should not be entered into the dictionary
            therfore if there are no answersets for any of the groups, a empty dictionary should be returned.
        '''
        self._fabricate_checklist(self.ethics_application)#checklist but no answers
        
        
        self.assertEqual(self.ethics_application._get_answersets_for_questionnaire(self.ethics_application.checklist), {})#no answers to anything so nothing in the dictionary
        
    def test__get_answersets_for_questionnaire_groups_with_data(self):
        '''
            If there are groups configured then for every group that has an aswerset there should be a record in 
            the database, the key should be the group, and the value is the answerset
        '''
        self._fabricate_checklist(self.ethics_application)#checklist but no answers
 
        
        #answers for checklist but not applciation form
        answer_set = self._fabricate_answerset(self.test_user, self.ethics_application.checklist)
        
        
        self.assertEqual(self.ethics_application._get_answersets_for_questionnaire(self.ethics_application.checklist),
                                                     {self.ethics_application.checklist.get_ordered_groups()[0]:answer_set})
        
    def test_get_answersets(self):
        '''
            This function should call _get_answersets_for_questionnaire twice,
            once for the checklist, and again for the application_form,
            concatenating the result
        '''
        
        
        self._fabricate_checklist(self.ethics_application)#checklist but no answers
        self._fabricate_application_form(self.ethics_application)
        
        with patch('ethicsapplication.models.EthicsApplication._get_answersets_for_questionnaire') as function_mock:
            function_mock.return_value = {'a':1}
            self.assertEqual(self.ethics_application.get_answersets(),{'a':1})
            self.assertEqual(function_mock.mock_calls, [call(self.ethics_application.checklist),
                                                        call(self.ethics_application.application_form)]
                             )
        
    def test_is_ready_to_submit_no_questionnaires(self):
        '''
            This test should simply return False if there are no questionnaires or groups for
            checklist and ethics application
        '''
        #no checklist or application form
        self.assertFalse(self.ethics_application.is_ready_to_submit())
        
    def test_is_ready_to_submit_no_asnwer_sets(self):
        '''
            If there are no answersets then this function should return False.
            It should return False as soon as it finds the first group without an answer
        '''
        
        with patch('ethicsapplication.models.EthicsApplication.get_answersets') as get_answersets_mock:
            
            answer_set_dict = MagicMock(name='answerset_dict')
            answer_set_dict.__contains__.return_value = False
            
            get_answersets_mock.return_value = answer_set_dict
            
            #checklist & applciation form incomplete
            self._fabricate_checklist(self.ethics_application)
            self._fabricate_application_form(self.ethics_application)
            
            self.assertFalse(self.ethics_application.is_ready_to_submit())
            
            self.assertEqual(answer_set_dict.__contains__.call_count ,1)
            self.assertEqual(get_answersets_mock.call_count , 1)
            
    def test_is_ready_to_submit_answer_sets_incomplete(self):
        '''
        '''
        with patch('ethicsapplication.models.EthicsApplication.get_answersets') as get_answersets_mock:
            
            answerset_mock = MagicMock(name='answerset')
            answerset_mock.is_complete.return_value = False
            
            answer_set_dict = MagicMock(name='answerset_dict')
            answer_set_dict.__getitem__.return_value = answerset_mock
            answer_set_dict.__contains__.return_value = True
            
            get_answersets_mock.return_value = answer_set_dict
            
            #checklist & applciation form incomplete
            self._fabricate_checklist(self.ethics_application)
            self._fabricate_application_form(self.ethics_application)
            
            self.assertFalse(self.ethics_application.is_ready_to_submit())
            
            self.assertEqual(answer_set_dict.__contains__.call_count, 1)
            self.assertEqual(answer_set_dict.__getitem__.call_count, 1)
            
            self.assertEqual(get_answersets_mock.call_count , 1)
            self.assertEqual(answerset_mock.mock_calls, [call.is_complete()])
        
    def test_is_ready_to_submit(self):
        '''
            This test should only return true is there is an answerset available for the checklist
            and every questiongroup in the applicationform. 
        
        '''
       
        with patch('ethicsapplication.models.EthicsApplication.get_answersets') as get_answersets_mock:
            
            answerset_mock = MagicMock(name='answerset')
            answerset_mock.is_complete.return_value = True
            
            answer_set_dict = MagicMock(name='answerset_dict')
            answer_set_dict.__getitem__.return_value = answerset_mock
            answer_set_dict.__contains__.return_value = True
            
            get_answersets_mock.return_value = answer_set_dict
            
            #checklist & applciation form incomplete
            self._fabricate_checklist(self.ethics_application)
            self._fabricate_application_form(self.ethics_application)
            
            self.assertTrue(self.ethics_application.is_ready_to_submit())
            answer_set_dict.__contains__.assert_any_call(self.ethics_application.checklist.get_ordered_groups()[0])
            answer_set_dict.__contains__.assert_any_call(self.ethics_application.application_form.get_ordered_groups()[0])
            
            answer_set_dict.__getitem__.assert_any_call(self.ethics_application.checklist.get_ordered_groups()[0])
            answer_set_dict.__getitem__.assert_any_call(self.ethics_application.application_form.get_ordered_groups()[0])
            
            self.assertEqual(get_answersets_mock.call_count , 1)
            self.assertEqual(answerset_mock.mock_calls, [call.is_complete(), call.is_complete()])
            
    def test_get_current_state(self):
        '''
            This function should return the name of the state that this application is currently in
            which is achieved by calling the get_state function from the workflows utils package
        '''
        
        with patch('ethicsapplication.models.get_state') as get_state_mock:
            test_state_name = 'test_state'
            get_state_mock.return_value = test_state_name
            
            test_application = EthicsApplication()
            self.assertEqual(test_application.get_current_state(), test_state_name)
            get_state_mock.assert_called_once_with(test_application)
            
    def test_assign_reviewer_user_is_none(self):
        '''
            If the user is None or anything that is not a user, then an attribute error is raised
        '''
        self.assertRaises(AttributeError, self.ethics_application.assign_reviewer, None)
        self.assertRaises(AttributeError, self.ethics_application.assign_reviewer, 'NotAUser')
        
    def test_assign_reviewer_setting_malconfigured(self):
        '''
            If the settings.REVIEWER_ROLE is not present in the settings module, or it is present but
            does not exist in the database then an ImporperlyConfigured error will be raised
        '''
        del(settings.REVIEWER_ROLE)
        self.assertRaises(ImproperlyConfigured, self.ethics_application.assign_reviewer, self.test_user)
        
        settings.REVIEWER_ROLE = 'InvalidRole'
        self.assertRaises(ImproperlyConfigured, self.ethics_application.assign_reviewer, self.test_user)
        
    def test_assign_reviewer_valid_user(self):
        '''
            if a valid user is passed in then the add_local_role function is used
            to assign this user to the reviewer role for this application
        '''
        with patch('ethicsapplication.models.add_local_role') as as_local_role_mock:
            
            self.ethics_application.assign_reviewer(self.test_user)
            as_local_role_mock.assert_called_once_with(self.ethics_application, self.test_user, Role.objects.get(name=settings.REVIEWER_ROLE))
        
class EthicsApplicationManagerTestCase(TestCase):
    
    def setUp(self):
        
        self.test_user = User.objects.create_user('test', 'me@home.com', 'password')
        self.ethics_application = EthicsApplication.objects.create(title='test_application', 
                                                                   principle_investigator=self.test_user)
        
    def test_get_active_applications_valid_user_with_applications(self):
        '''
            If the user is valid and has applications this function should return a list of these applications objects
        '''
        
        
        test_application_2 = EthicsApplication(title='test application', principle_investigator=self.test_user)
        test_application_2.save()
        
        self.assertEqual([self.ethics_application, test_application_2], 
                         EthicsApplication.objects.get_active_applications(self.test_user)) 
        
    def test_get_active_applications_valid_user_no_applications(self):
        '''
            If the user is valid but has no applications this function will return an empty list
        '''
        a_user = User.objects.create_user('a_user', 'email@email.com', 'password')
        
        self.assertEqual([], EthicsApplication.objects.get_active_applications(a_user)) 
        
         
    def test_get_active_applications_valid_user_inactive_applications(self):
        '''
            If the user is valid but has some active and also inactive applications, only the active 
            applications should be returned.
        '''
        
       
        #create an inactive application
        EthicsApplication.objects.create(title='test application', principle_investigator=self.test_user,
                                                               active=False)

        
        self.assertEqual([self.ethics_application], 
                         EthicsApplication.objects.get_active_applications(self.test_user))
        
class GetApplicationsForReviewTests(TestCase):
    
    def setUp(self):
        
        self.test_user = User.objects.create_user('test', 'me@home.com', 'password')
        self.ethics_application = EthicsApplication.objects.create(title='test_application', 
                                                                   principle_investigator=self.test_user)
        self.test_state = State.objects.create(name='test_state', workflow=Workflow.objects.create(name='test'))
    
    def test_malconfigured(self):
        '''
            If the settings.REVIEWER_ROLE is not present in the settings module, or it is present but
            does not exist in the database then an ImporperlyConfigured error will be raised
        '''
        del(settings.REVIEWER_ROLE)
        self.assertRaises(ImproperlyConfigured, EthicsApplication.objects.get_applications_for_review, self.test_user)
        
        settings.REVIEWER_ROLE = 'InvalidRole'
        self.assertRaises(ImproperlyConfigured, EthicsApplication.objects.get_applications_for_review, self.test_user)
        
        
    @patch('ethicsapplication.models.get_object_for_principle_as_role')
    def test_no_state_specified(self, util_patch):
        '''
           This function is basically a very thin wrapper around the 
           get_object_for_principle_as_role utility function provided by django-permission
           library. Therefore this function should return whatever this function does.
           
           The value add of this function is that it knows how to look up the role to be
           used for the reviewer, this should be looked up based on the settings.REVIEWER_ROLE
        '''
        
        settings.REVIEWER_ROLE = 'Reviewer'
        reviewer_role = Role.objects.get(name=settings.REVIEWER_ROLE)
        
        util_patch.return_value = [1,2,3]
        
        self.assertEqual(EthicsApplication.objects.get_applications_for_review(self.test_user), 
                         [1,2,3])
        
        util_patch.assert_called_once_with(principle=self.test_user, principle_role=reviewer_role)
        
    @patch('ethicsapplication.models.get_object_for_principle_as_role')
    def test_state_specified_as_string(self, util_patch):
        '''
            If the state is specified as a String then this should first be resplved to a State object
            if this is not possible then None should be used as the state (and so all the applications
            will be returned).
            If the state is a State object (or the state can be resolved by the string name) then the list
            of applications should be filtered to only include the applications that are in this given state.
        '''
        settings.REVIEWER_ROLE = 'Reviewer'
        util_patch.return_value = [1]
        
        #invalid String
        with patch('ethicsapplication.models.get_state') as get_state_mock:
            
            #invalid state string first
            EthicsApplication.objects.get_applications_for_review(self.test_user, state='invalid')
            self.assertEqual(get_state_mock.call_count, 0)
            
            #now try again with a valid string
            EthicsApplication.objects.get_applications_for_review(self.test_user, state='test_state')
            get_state_mock.assert_called_once_with(1)
        
    @patch('ethicsapplication.models.get_object_for_principle_as_role')  
    def test_statet_specified_as_role(self, util_patch):
        
        
        settings.REVIEWER_ROLE = 'Reviewer'
        reviewer_role = Role.objects.get(name=settings.REVIEWER_ROLE)
        
        util_patch.return_value = [1,2,3]
        
        with patch('ethicsapplication.models.get_state') as get_state_mock:
            get_state_returns = ['a different state', self.test_state, self.test_state]
            
            def sideEffect(*args, **kwargs):
                return get_state_returns.pop(0)
            
            get_state_mock.side_effect = sideEffect
            
            applications = EthicsApplication.objects.get_applications_for_review(self.test_user, state='test_state')
            
            self.assertEqual(applications,[2,3])
        
            util_patch.assert_called_once_with(principle=self.test_user, principle_role=reviewer_role)
            self.assertEqual(get_state_mock.mock_calls, [call(1), call(2), call(3)])
            
            
            
            
