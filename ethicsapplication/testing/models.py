'''
This will test the model code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''


from django.test import TestCase

class ModelsTest(TestCase):
    
    
    def test_valid_EthicsApplication_creation(self):
        '''
            You should be able to create a valid EthicsApplication
            with:
            1. Title (less than 255 characters)
            2. Principle Investigator
            3. No application
        
        '''
        self.assert_(False, 'NOt yet implemented')

    def test_invalid_EthicsApplication_creation_no_title(self):
        '''
            If you don't supply a title then you will get an exception
        '''
        self.assert_(False, 'NOt yet implemented')
        
    def test_invalid_EthicsApplication_creation_no_pi(self):
        '''
            If you don't supply a principle investigator then you will get an exception
        '''
        self.assert_(False, 'Not yet implemented')
        