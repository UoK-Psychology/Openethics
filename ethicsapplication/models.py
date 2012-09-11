from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import AnswerSet, Questionnaire
from django.db.models.manager import Manager

# Create your models here.

class EthicsApplicationManager(Manager):
    
    def get_active_applications(self, the_user):
        '''
            Returns the active applications for a user, will return an empty list if there
            aren't any active users.
        
        '''
        
        return [x for x in super(EthicsApplicationManager, self).get_query_set().filter(principle_investigator=the_user).filter(active=True)]

class EthicsApplication(models.Model):
    '''
        This defines an ethics application, it is the root model object
        from which all other information about the application can be found.
        It is thisobject that will be manipulated by the workflow engine.   
    '''
    
    title = models.CharField(max_length=255)
    principle_investigator = models.ForeignKey(User ,related_name='pi')
    application_form = models.ForeignKey(AnswerSet, related_name='application_form', blank=True, null=True)
    active = models.BooleanField(default=True)
    checklist = models.ForeignKey(Questionnaire, related_name='checklist_questionnaire', blank=True, null=True)
    #TODO test the new checklist attribute
    objects = EthicsApplicationManager()
    def __unicode__(self):
        return '%s, PI:%s' % (self.title, self.principle_investigator.username)
    
