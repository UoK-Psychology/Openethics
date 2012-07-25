'''
This will test the forms code for the ethicsapplication application

Created on Jul 25, 2012

@author: jasonmarshall
'''

from django.test import TestCase
from ethicsapplication.forms import EthicsApplicationForm

class FormsTest(TestCase):
    
    def test_EthicsApplication_form_title(self):
        '''
            Check that the form provides a field that cannot be blank for the 
            application title
        '''
        form = EthicsApplicationForm()
        
        self.assertTrue('title' in form.fields)

    def test_EthicsApplication_form_ignored_fields(self):
        '''
            Check that the form does not display a field for either 
            Principle investigator, nor application.
        '''
        form = EthicsApplicationForm()
        
        self.assertFalse('principle_investigator' in form.fields)
        self.assertFalse('application_form' in form.fields)
        
    def test_EthicsApplication_form_title_must_be_present(self):
        '''
            The form must require a non blank string for the title field.
        '''
        incorrect_data = {'data': {'title': '',}}
        form = EthicsApplicationForm(incorrect_data)
        
        form.is_valid()
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['title'], [u'This field is required.'])
