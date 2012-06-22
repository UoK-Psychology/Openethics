from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models.fields import DateField
import datetime
from django.contrib.auth.models import User
from registration import forms



class index_test(TestCase):
    
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200, 'Index page should be shown')
        #self.assertEqual(resp.templates[0].name, '404.html', 'The standard 404 template should be used')


   