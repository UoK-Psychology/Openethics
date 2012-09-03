'''
This will test the model code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''


from django.test import TestCase
from ethicsapplication.models import EthicsApplication, EthicsApplicationManager
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.conf import settings
from mock import patch
from django.core.exceptions import ImproperlyConfigured
from workflows.models import Workflow

class EthicsApplicationModelTestCase(TestCase):
    
    def setUp(self):
        settings.APPLICATION_WORKFLOW = 'Ethics_Application_Approval'
    
    def test_valid_EthicsApplication_creation(self):
        '''
            You should be able to create a valid EthicsApplication
            with:
            1. Title (less than 255 characters)
            2. Principle Investigator
            3. No application
            
            The active flag should default to True
        
        '''
        
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
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
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        my_Application = EthicsApplication(title='test', principle_investigator=a_user)
        my_Application.save()
        #assert that it was called once
        patched_function.assert_called_once_with()
        
        #make a change and save, the patch should not be called again!
        my_Application.title = 'changed'
        my_Application.save()
        
        patched_function.assert_called_once_with()
        
        
        self.assertTrue(False)
        
        
    def test_add_to_workflow_setting_absent(self):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow defined in the settings.APPLICATION_WORKFLOW setting. In this case
            the setting is not present so an ImproperlyConfigured exception is raised
        
        ''' 
        settings.APPLICATION_WORKFLOW = None
        test_application = EthicsApplication(title='test', principle_investigator=User.objects.create_user('test', 'me@home.com', 'password'))
        self.assertRaises(ImproperlyConfigured, test_application._add_to_workflow)
        
    def test_add_to_workflow_setting_invalid(self):
        '''
            If this is a new EthicsApplication object then it should be added to the 
            workflow defined in the settings.APPLICATION_WORKFLOW setting. In this case
            the setting is present but the workflow doesn't exist in the db so an ImproperlyConfigured
            exception is raised.
        
        ''' 
        
        settings.APPLICATION_WORKFLOW = 'Does not exist!'
        test_application = EthicsApplication(title='test', principle_investigator=User.objects.create_user('test', 'me@home.com', 'password'))
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
        test_application = EthicsApplication(title='test', principle_investigator=User.objects.create_user('test', 'me@home.com', 'password'))
        test_application.save()
        set_workflow_mock.assert_called_once_with(test_application, approval_workflow)
        
    def test_update_principle_investigator(self):
        '''
            When the principle investigator setter is called succesfully the 
            _add_to_principle_investigator_role function should be called to update the 
            membership of this group
        '''
        self.assertTrue(False)
    
    def test_absent_PI_role_in_settings(self):
        '''
            test that if there settings.PRINCIPLE_INVESTIGATOR_ROLE is not present
            or doesn't exist in the db then a ImproperlyCOnfigured exception should be raised.
        '''
        self.assertTrue(False)
        
    def test_add_to_principle_investigator_role_new_user_with_previous(self):
        '''
            If there is already a user in the PI role and the new user is not this user then
            the existing user should be removed, and the new user added in her place.
        '''
        self.assertTrue(False)
    def test_add_to_principle_investigator_role_new_user_no_previous(self):
        '''
            If there is no previous user in the PI role then the new user should be added into
            the PI role for this instance of ethics application
        '''
        self.assertTrue(False)
        
    def test_add_to_principle_investigator_role_existing_user(self):
        '''
            If the current user in the PI role is the same as the existing one then nothing should 
            happen.
        '''
        settings.PRINCIPLE_INVESTIGATOR_ROLE = 'pi'
        #the fixture defines ethics application 3 that has user 3 as the only member of the PI group
        #get application 3
        #get user 3
        
        self.assertTrue(False)
        
        
        
class EthicsApplicationManagerTestCase(TestCase):
    
    def test_get_active_applications_invalid_user(self):
        '''
            If the user is invalid this function should just return an empty list
        '''
        #create a user but don't save it
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        
        self.assertEqual([], EthicsApplication.objects.get_active_applications(a_user))  
        
    def test_get_active_applications_valid_user_with_applications(self):
        '''
            If the user is valid and has applications this function should return a list of these applications objects
        '''
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        a_user.save()#save the user so it becomes a valid user
        
        test_application_1 = EthicsApplication(title='test application', principle_investigator=a_user)
        test_application_1.save()
        
        test_application_2 = EthicsApplication(title='test application', principle_investigator=a_user)
        test_application_2.save()
        
        self.assertEqual([test_application_1, test_application_2], 
                         EthicsApplication.objects.get_active_applications(a_user)) 
        
    def test_get_active_applications_valid_user_no_applications(self):
        '''
            If the user is valid but has no applications this function will return an empty list
        '''
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        a_user.save()#save the user so it becomes a valid user
        self.assertEqual([], EthicsApplication.objects.get_active_applications(a_user)) 
        
         
    def test_get_active_applications_valid_user_inactive_applications(self):
        '''
            If the user is valid but has some active and also inactive applications, only the active 
            applications should be returned.
        '''
        
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        a_user.save()#save the user so it becomes a valid user
        
        test_application_1 = EthicsApplication(title='test application', principle_investigator=a_user)
        test_application_1.save()
        
        test_application_2 = EthicsApplication(title='test application', principle_investigator=a_user, active=False)
        test_application_2.save()
        
        self.assertEqual([test_application_1], 
                         EthicsApplication.objects.get_active_applications(a_user)) 