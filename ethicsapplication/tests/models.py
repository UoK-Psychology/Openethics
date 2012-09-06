'''
This will test the model code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''


from django.test import TestCase
from ethicsapplication.models import EthicsApplication, EthicsApplicationManager
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

class EthicsApplicationModelTestCase(TestCase):
    
    
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

    def test_invalid_EthicsApplication_creation_no_title(self):
        '''
            If you don't supply a title then you will get an exception
        '''
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        ethicsApplication = EthicsApplication( principle_investigator=a_user)
        
        self.assertRaises(IntegrityError, ethicsApplication.save)

    def test_ethicsapplication_manager(self):
        
        '''
            The default manager for an ethicsapplication should be an instance of EthicsApplicationManager
            which is a custom manager that adds some table level functionality.
        '''
        self.assertIsInstance(EthicsApplication.objects, EthicsApplicationManager)  
        
        
        
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