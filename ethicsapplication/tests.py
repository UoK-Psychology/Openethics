'''
Created on Jul 25, 2012

@author: jasonmarshall
'''
from django.utils.unittest.loader import TestLoader
from testing import views as viewTests, forms as formsTest, models as modelTests
from django.utils.unittest.suite import TestSuite

def suite():
    
    views_suite = TestLoader().loadTestsFromModule(viewTests, True)
    forms_suite = TestLoader().loadTestsFromModule(formsTest, True)
    models_suite = TestLoader().loadTestsFromModule(modelTests, True)
    
    return TestSuite([views_suite,forms_suite,models_suite])
    