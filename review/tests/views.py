from django.test import TestCase
from django.core.urlresolvers import reverse
from ethicsapplication.models import EthicsApplication
from django.contrib.auth.models import User
from mock import patch, MagicMock
from mock_django.signals import mock_signal_receiver
from review.signals import application_submitted_for_review


class SubmitForReviewTests(TestCase):
    
    def setUp(self):
        
        self.test_user = User.objects.create_user('test', 'test@test.com', 'password')
        self.ethicsApplication = EthicsApplication.objects.create(title='test application', principle_investigator=self.test_user)
        
        
    def test_not_logged_in(self):
        '''
            If there is no user logged in then this should return a forbidden exception
        '''
        url = reverse('submit_application', kwargs={'ethics_application_id':self.ethicsApplication.id})
        response = self.client.get(url)
        self.assertEquals (403, response.status_code )
    
    def test_invalid_ethics_id(self):
        '''
            A 404 exception should be thrown if an ethicsapplciation for the passed in 
            ethics_application_id doesn't exist
        '''
        url = reverse('submit_application', kwargs={'ethics_application_id':999999})
        response = self.client.get(url)
        self.assertEquals (404, response.status_code )
        
    def test_wrong_permissions(self):
        '''
            If the logged in user doesn't have the submit permission for the ethics application
            then a forbidden exception should be raised
        '''
        self.client.login(username='test', password='password') 
        
        with patch('review.views.has_permission') as has_permission_mock:
            has_permission_mock.return_value = False
            
            url = reverse('submit_application', kwargs={'ethics_application_id':self.ethicsApplication.id})
            response = self.client.get(url)
            self.assertEquals (403, response.status_code )
            has_permission_mock.assert_called_once_with(self.ethicsApplication, self.test_user, 'submit')
        
    def test_forbidden_transition(self):
        '''
            If the ethics application cannot do the submit_for_review transition then a forbidden exception should be thrown
        '''
        self.client.login(username='test', password='password') 
        with patch('review.views.has_permission') as has_permission_mock:
            has_permission_mock.return_value = True
            
            with patch('review.views.do_transition') as do_transition_mock:
                do_transition_mock.return_value = False
                
                url = reverse('submit_application', kwargs={'ethics_application_id':self.ethicsApplication.id})
                response = self.client.get(url)
                self.assertEquals (403, response.status_code)
                do_transition_mock.assert_called_once_with(self.ethicsApplication, 'submit_for_review', self.test_user)
                has_permission_mock.assert_called_once_with(self.ethicsApplication, self.test_user, 'submit')
    
     
    @patch('review.views.has_permission')
    @patch('review.views.do_transition')  
    @patch('review.models.CommitteeManager.get_next_free_reviewer')
    @patch('ethicsapplication.models.EthicsApplication.assign_reviewer')
    def test_correct_state_reviewer(self, assign_reviewer_mock, get_next_free_reviewer_mock,do_transition_mock,has_permission_mock ):
        '''
            If all is well and the application can perform the submit_for_review transition then this function
            should call the do_transition function, then it shoudl find the next avaialble reviewer
            using the CommitteeManager.get_next_free_reviewer, assigning this user as a reviewer on the application
            using the assign_reviewer function and return to the home page.
            
            This function should also dispatch the application_submitted signal
        '''
        
        with mock_signal_receiver(application_submitted_for_review) as submission_receiver:
            self.client.login(username='test', password='password') 
            
            has_permission_mock.return_value = True
            do_transition_mock.return_value = True
            next_free_reviewer = MagicMock(name='free_reviewer')
            get_next_free_reviewer_mock.return_value = next_free_reviewer
            
            
            url = reverse('submit_application', kwargs={'ethics_application_id':self.ethicsApplication.id})
            response = self.client.get(url)
            self.assertRedirects(response, reverse('index_view'))
            do_transition_mock.assert_called_once_with(self.ethicsApplication, 'submit_for_review', self.test_user)
            has_permission_mock.assert_called_once_with(self.ethicsApplication, self.test_user, 'submit')
            get_next_free_reviewer_mock.assert_called_once_with()
            assign_reviewer_mock.assert_called_once_with(next_free_reviewer)
            
            submission_receiver.assert_called_once_with(application=self.ethicsApplication,
                                                        reviewer=next_free_reviewer,
                                                        sender=None,
                                                        signal=application_submitted_for_review)

class EvaluateApplicationFormTests(TestCase):
    
    def setUp(self):
        '''
            The common setup for all tests
        '''
        self.test_user = User.objects.create_user('test', 'teset@test.com', 'password')
        self.test_application = EthicsApplication.objects.create(title='test', principle_investigator=self.test_user)
        self.valid_accept_url = reverse('accept_application', kwargs={'ethics_application_id':self.test_application.id})
        self.valid_reject_url = reverse('reject_application', kwargs={'ethics_application_id':self.test_application.id})
        self.valid_url_permutations = [self.valid_accept_url, self.valid_reject_url]
    def test_logged_in(self):
        '''
            If the user is not logged in then they should eb redirected to the login
            screen
        '''
        #accept url
        for url in self.valid_url_permutations:
            response = self.client.get(url)
            self.assertRedirects(response, '/accounts/login/?next=%s' % url )
        
        
        
    def test_invalid_parameters(self):
        '''
            If the ethics_application_id is not in the db then this should cause a 
            404 error.
        '''
        self.client.login(username='test', password='password') 
        invalid_url_permutations = [reverse('accept_application', kwargs={'ethics_application_id':999}),
                                    reverse('reject_application', kwargs={'ethics_application_id':999})]
        
        for url in invalid_url_permutations:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
        
    
    
    def shared_asserions(self, url, expected_transition):
        '''
            Depending on what url (accept or reject) is hit with a valid ethics_application_id 
            then the do transition should be called with the requesting user,
            the ethics application and the transition codename represented by expected_transition
            
            If this returns False then a 403 forbidden error should be raised
            If this returns True then the request should be redirected to the index
            page.
        
        '''
        self.client.login(username='test', password='password') 
        with patch('review.views.do_transition') as do_transition_mock:
            do_transition_mock.return_value = False
            
            response = self.client.get(url)
            
            do_transition_mock.assert_called_with(self.test_application, expected_transition, self.test_user)
            self.assertEqual(response.status_code, 403)
            
            do_transition_mock.reset()
            do_transition_mock.return_value = True
            response = self.client.get(url)
            self.assertRedirects(response, reverse('index_view'))
            
           
    def test_accept(self):
        '''
            run the shared assertions for the accept url
        '''
        
        self.shared_asserions(self.valid_accept_url, 'approve')
    def test_reject(self):
        '''
            run the shared assertions for the rejected url
        '''
        self.shared_asserions(self.valid_reject_url, 'reject')   
