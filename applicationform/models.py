from django.db import models
from questionnaire.models import Question, QuestionGroup



class FullApplicationChecklistLinkManager(models.Manager):
    
    def get_ordered_groups_for_question(self, the_question):
        '''
            Returns all of the Groups that are linked to a particular 
            checklist_question, in order.
        '''
        
        return [link.included_group for link in super(FullApplicationChecklistLinkManager, self).
                get_query_set().filter(checklist_question=the_question).order_by('order')]
        
        



class FullApplicationChecklistLink(models.Model):
    '''
        This model encapsulates the link between a checklist question
        and one of more QuestionGroups that will be added to the
        ethics application_form if that question is answered yes.    
    '''
    
    checklist_question = models.ForeignKey(Question, related_name='checklist_question')
    included_group = models.ForeignKey(QuestionGroup, related_name='included_group')
    order = models.IntegerField()
    objects = FullApplicationChecklistLinkManager()


