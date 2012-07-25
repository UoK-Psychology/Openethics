'''
This will test the forms code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''

from django.test import TestCase

class FormsTest(TestCase):
    
    def test_EthicsApplication_form_title(self):
        '''
            Check that the form provdes a field that cannot be blank for the 
            application title
        '''
        
        self.assert_(False, 'Not yet implemented')

    def test_EthicsApplication_form_ignored_fields(self):
        '''
            Check that the form does not display a field for either 
            Principle investigator, nor application.
        '''
        self.assert_(False, 'Not yet implemented')
