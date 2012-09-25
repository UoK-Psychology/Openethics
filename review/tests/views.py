from django.test import TestCase


class SubmitForReviewTests(TestCase):
    
    def test_not_logged_in(self):
        '''
            If there is no user logged in then this should return a forbidden exception
        '''
        self.assertTrue(False)
    
    def test_invalid_ethics_id(self):
        '''
            A 404 exception should be thrown if an ethicsapplciation for the passed in 
            ethics_application_id doesn't exist
        '''
        self.assertTrue(False)
        
    def test_wrong_permissions(self):
        '''
            If the logged in user doesn't have the submit permission for the ethics application
            then a forbidden exception should be raised
        '''
        self.assertTrue(False)
    
        
    def test_incorrect_state(self):
        '''
            If the ethics application cannot do the transition to "in review" due to its current
            state then a forbidden exception should be thrown
        '''
        self.assertTrue(False)
        
    def test_correct_state_no_reviewers(self):
        '''
            If there are no reviewers configured then a configuration error should be raised 
        '''
        self.assertTrue(False)
        
    def test_correct_state_reviewer(self):
        '''
            If all is well then the ethics application should be transitioned to the 
            'in review' state, and the reviewer returned from the get_next_reviewer function
            should be added as a member of the reviewer role for this application
        '''
        self.assertTrue(False)
        
