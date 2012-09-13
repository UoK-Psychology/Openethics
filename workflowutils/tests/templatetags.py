from django.test import TestCase
from django.template.base import Template
from django.template.context import Context
from mock import MagicMock, patch
from django.contrib.auth.models import User



class HasPermissionTagTestCase(TestCase):
    
    def setUp(self):
        
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        
    @patch('workflowutils.templatetags.token_tags.has_permission')
    def test_object_has_permission(self, has_permission_mock):
        '''
            If the user does indeed have the permission for that passed in object then the
            template tag should print it's payload 
        '''
        
        #patch the has_permission function
        has_permission_mock.return_value = True
        
        token = MagicMock(name='token_mock')
        token.resolve.return_value = token
        
        t = Template('''{% load token_tags %}{% if_has_permission_for_object token view %}test worked!{% end_if_has_permission_for_object %}''')
        
        c = Context({"token": token, 'user':self.user})
        output = t.render(c)
        self.assertEqual(output, 'test worked!')
        has_permission_mock.assert_called_with(token,self.user, 'view')
        
    @patch('workflowutils.templatetags.token_tags.has_permission')
    def test_object_doesnt_have_permission_without_else(self, has_permission_mock):
        '''
            If the user doesn't have the permission for this object , and there is no else clause specified the 
            tag should render nothing
        '''
        
        has_permission_mock.return_value = False
        
        token = MagicMock(name='token_mock')
        token.resolve.return_value = token
        
        t = Template('''{% load token_tags %}{% if_has_permission_for_object token view %}test didn't work{% end_if_has_permission_for_object %}''')
        
        c = Context({"token": token, 'user':self.user})
        output = t.render(c)
        self.assertEqual(output, '')#shouldn't render anything as there isn't an else
        has_permission_mock.assert_called_with(token,self.user, 'view')


    @patch('workflowutils.templatetags.token_tags.has_permission')
    def test_object_doesnt_have_permission_with_else(self, has_permission_mock):
        '''
            If the user doesn't have the permission for this object , but there is an else clause specified the 
            tag should render the payload of that clause
        '''
        
        has_permission_mock.return_value = False
        
        token = MagicMock(name='token_mock')
        token.resolve.return_value = token
        
        t = Template('''{% load token_tags %}{% if_has_permission_for_object token view %}test didn't work{%else%}test worked!{% end_if_has_permission_for_object %}''')
        
        c = Context({"token": token, 'user':self.user})
        output = t.render(c)
        self.assertEqual(output, 'test worked!')
        has_permission_mock.assert_called_with(token,self.user, 'view')
