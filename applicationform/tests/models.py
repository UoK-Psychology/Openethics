from django.test import TestCase
from applicationform.models import FullApplicationChecklistLink,\
    FullApplicationChecklistLinkManager
from questionnaire.models import QuestionGroup, Question
from django.db.utils import IntegrityError


class FullApplicationChecklistLinkTestCase(TestCase):

    
    def test_fields(self):
        '''
            This model should specify the following fields:
            checklist_question - ForeignKey(Question)
            included_group - ForeignKey (QuestionGroup)
            order - Integer
            
            all of which are required for creation
        '''
        
        test_question = Question.objects.create(label='test', field_type='charfield')
        test_question_group = QuestionGroup.objects.create(name='test')
        
        self.assertRaises(IntegrityError, FullApplicationChecklistLink.objects.create)
        self.assertRaises(IntegrityError, FullApplicationChecklistLink.objects.create, checklist_question=test_question)
        self.assertRaises(IntegrityError, FullApplicationChecklistLink.objects.create, checklist_question=test_question, included_group=test_question_group)
        self.assertTrue( FullApplicationChecklistLink.objects.create(checklist_question=test_question, included_group=test_question_group, order=1) )
        
    def test_default_manager(self):
        '''
            This model should have an instance of  FullApplicationChecklistLinkManager
            as the default manager available through the ''objects'' field.
        '''
        self.assertIsInstance(FullApplicationChecklistLink.objects, FullApplicationChecklistLinkManager)
        
    
class FullApplicationChecklistLinkManagerTestCase(TestCase):
    def setUp(self):
        self.test_question = Question.objects.create(label='test', field_type='charfield')
        self.test_first_group = QuestionGroup.objects.create(name='group1')
        self.test_second_group = QuestionGroup.objects.create(name='group2')
        
    def test_get_ordered_groups_for_question_no_links(self):
        '''
            If there are no links avaialble questions matching
            the query then this function should return an empty list
        '''
        self.assertEqual(FullApplicationChecklistLink.objects.get_ordered_groups_for_question(self.test_question), [])
        
    def test_get_ordered_groups_for_question_links(self):
        '''
            If there are links avaialble then this function should return
            all of them in a list, which is ordered by the order field on the 
            FullApplicationChecklistLink objects.
        '''
        FullApplicationChecklistLink.objects.create(checklist_question=self.test_question, included_group=self.test_first_group, order=1)
        self.assertEqual(FullApplicationChecklistLink.objects.get_ordered_groups_for_question(self.test_question),
                          [self.test_first_group,])
        
        FullApplicationChecklistLink.objects.create(checklist_question=self.test_question, included_group=self.test_second_group, order=1)
        self.assertEqual(FullApplicationChecklistLink.objects.get_ordered_groups_for_question(self.test_question),
                          [self.test_first_group,self.test_second_group,])
        



