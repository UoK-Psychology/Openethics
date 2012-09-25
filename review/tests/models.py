from django.test import TestCase
from django.db.utils import IntegrityError
from review.models import Committee
from django.contrib.auth.models import User

class CommitteeTestCase(TestCase):
    
    def test_fields(self):
        '''
            This model requires a committee member
            and the optional count should default to 0.
        '''
        
        self.assertRaises(IntegrityError, Committee.objects.create)
        committee = Committee.objects.create(member=User.objects.create_user('username', 'email@me.com', 'password'))
        self.assertEquals(committee.count, 0)
