from django.test import TestCase


class FullApplicationChecklistLinkTestCase(TestCase):

    
    def test_fields(self):
        '''
            This model should specify the following fields:
            checklist_question - ForeignKey(Question)
            included_group - ForeignKey (QuestionGroup)
            order - Integer
            
            all of which are required for creation
        '''
        self.assertTrue(False)
        
    def test_default_manager(self):
        '''
            This model should have an instance of  FullApplicationChecklistLinkManager
            as the default manager available through the ''objects'' field.
        '''
        self.assertTrue(False)
    
class FullApplicationChecklistLinkManagerTestCase(TestCase):

    
    def test_get_ordered_groups_for_question_no_links(self):
        '''
            If there are no links avaialble questions matching
            the query then this function should return an empty list
        '''
        self.assertTrue(False)
        
    def test_get_ordered_groups_for_question_links(self):
        '''
            If there are links avaialble then this function should return
            all of them in a list, which is ordered by the order field on the 
            FullApplicationChecklistLink objects.
        '''
        self.assertTrue(False)


