'''
This will test all the view code for the ethicsapplication application

Created on Jul 25, 2012
@author: jasonmarshall
'''


from django.test import TestCase
from django.core.urlresolvers import reverse
from ethicsapplication.forms import EthicsApplicationForm
from django.contrib.auth.models import User
from ethicsapplication.models import EthicsApplication


class ViewsTest(TestCase):
    
    def setUp(self):
        user = User.objects.create_user('test', 'test@home.com', 'testpass')
        user.save()
        
    
    def test_create_Application_not_logged_in(self):
        '''
            If there is no user logged in, you should be redirected to the login url
        '''
        response = self.client.get(reverse('create_application_view'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('create_application_view') )
        
    def test_create_application_get(self):
        '''
            A GET request to the create_application_view url should if the user logged in:
            
            1. Return a http 200 status code.
            2. Use the template ethicsapplication/create.html.
            3. Have a form object in the context.
        '''
        self.client.login(username='test', password='testpass')   
        response = self.client.get(reverse('create_application_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'ethicsapplication/create.html')
        self.failUnless(isinstance(response.context['form'],
                                   EthicsApplicationForm))
        
    def test_create_application_valid_post(self):
        '''
            A valid post to this view, for a user that is logged in
            should consist of:
            1. a title
            
            and should:
            1. Create a new Ethics Application in the databse
            2. return http 302 (redirect)
            3. should redirect to the view application page for the new application
        '''
        post_data = {}
        self.client.login(username='test', password='testpass')   
        response = self.client.post(reverse('create_application_view'),post_data)
        applications = EthicsApplication.objects.all()
        
        self.assertTrue(len(applications) ==1)
        self.assertRedirects(response, reverse('application-view', {'application_id':applications[0].id}))
        
        
    def test_create_application_invalid_post(self):
        '''
            An invalid post to this view, for a user that is logged in
            should consist of:
            1. no title
            
            and should:
            1. not create a new Ethics Application in the databse
            2. render the form bound to the previous answers
            3. have an error in the form for not supplying a title
        '''
        self.assert_(False, 'Not yet implemented')
        
        
    