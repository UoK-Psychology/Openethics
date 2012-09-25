from django.test import TestCase

class CommitteeTestCase(TestCase):
    
    def test_fields(self):
        '''
            This model requires a committee member
            and the optional count should default to 0.
        '''
        self.assertTrue(False)
