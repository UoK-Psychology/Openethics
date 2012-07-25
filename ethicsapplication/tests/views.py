'''
This will test all the view code for the ethicsapplication application

Created on Jul 25, 2012
@author: jasonmarshall
'''


from django.test import TestCase
from django.core.urlresolvers import reverse
from ethicsapplication.forms import EthicsApplicationForm


class ViewsTest(TestCase):
    
    def test_create_application_get(self):
        '''
            A GET request to the create_application_view url should:
            
            1. Return a http 200 status code.
            2. Use the template ethicsapplication/create.html.
            3. Have a form object in the context.
        '''
        response = self.client.get(reverse('create_application_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'ethicsapplication/create.html')
        self.failUnless(isinstance(response.context['form'],
                                   EthicsApplicationForm))