from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import AnswerSet

# Create your models here.


class EthicsApplication(models.Model):
    '''
        This defines an ethics application, it is the root model object
        from which all other information about the application can be found.
        It is thisobject that will be manipulated by the workflow engine.   
    '''
    
    title = models.CharField(max_length=255)
    principle_investigator = models.ForeignKey(User ,related_name='pi')
    application_form = models.ForeignKey(AnswerSet, related_name='application_form', blank=True, null=True)
    
    def __unicode__(self):
        return '%s, PI:%s' % (self.title, self.principle_investigator.username)