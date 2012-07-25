'''
This will test the model code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''


from django.test import TestCase
from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

class ModelsTest(TestCase):
    
    
    def test_valid_EthicsApplication_creation(self):
        '''
            You should be able to create a valid EthicsApplication
            with:
            1. Title (less than 255 characters)
            2. Principle Investigator
            3. No application
        
        '''
        a_user = User.objects.create_user('test', 'me@home.com', 'password')
        ethicsApplication = EthicsApplication(title='test application', principle_investigator=a_user)
        ethicsApplication.save()
        
        self.assertTrue(ethicsApplication.title == 'test application')
        self.assertTrue(ethicsApplication.principle_investigator == a_user)
        self.assertTrue(ethicsApplication.application_form == None)
        
    def test_invalid_EthicsApplication_creation_no_pi(self):
        '''
            If you don't supply a principle investigator then you will get an exception
        '''
        ethicsApplication = EthicsApplication(title='test application')

        self.assertRaises(IntegrityError, ethicsApplication.save)
        
        