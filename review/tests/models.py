from django.test import TestCase
from django.db.utils import IntegrityError
from review.models import Committee, CommitteeManager
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
        
    def test_default_manager(self):
        '''
            The committee model should have an instance of CommitteeManager as its deafult manager
        ''' 
        self.assertIsInstance(Committee.objects, CommitteeManager)

class CommitteeManagerTestCase(TestCase):
    
    def test_get_next_free_reviewer_no_reviewers(self):
        '''
            If there are no reviewers in the database then this function should just return None
        '''
        self.assertIsNone(Committee.objects.get_next_free_reviewer())
        
    def test_get_next_free_reviewer(self):
        '''
            This function should return the reviewer that has the smallest count.
            If two reviewers have the same count then then the reviewer with the largest primary
            key is returned.
        '''
        
        reviewer1 = User.objects.create_user('user1', 'test@test.com', 'password')
        reviewer2 = User.objects.create_user('user2', 'test@test.com', 'password')
        reviewer3 = User.objects.create_user('user3', 'test@test.com', 'password')
        
        reviewers = [(reviewer1, 5), (reviewer2, 0), (reviewer3, 2)]
        
        commiteeMap = {}
        for reviewer in reviewers:
            commiteeMap[reviewer[0]] = Committee.objects.create(member = reviewer[0] , count = reviewer[1])
            
        #currently the reviewer 2 should be returned
        self.assertEqual(Committee.objects.get_next_free_reviewer(), reviewer2)
        
        #now change reviewr3's count to 0, this would mean that reviewer 3 would be returned as their pk is higher
        commiteeMap[reviewer3].count = 0
        
        self.assertEqual(Committee.objects.get_next_free_reviewer(), reviewer3)
        
        
        
        