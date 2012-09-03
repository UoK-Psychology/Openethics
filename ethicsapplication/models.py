from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import AnswerSet
from django.db.models.manager import Manager
from workflows.utils import set_workflow
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from workflows.models import Workflow

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
    
    objects = EthicsApplicationManager()
    
    def save(self):
        
        starting_id = self.id
        
        super(EthicsApplication, self).save()
        
        if(starting_id != self.id): #not entirely fool proof as you could create an instance with an explicit id, but you shouldn't do that
            self._add_to_workflow()
            
            
    def __unicode__(self):
        return '%s, PI:%s' % (self.title, self.principle_investigator.username)
    


    def _add_to_workflow(self):
        '''
            Adds the EthicsApplication to the workflow that is defined in Settings.APPLICATION_WORKFLOW
            Will raise an ImproperlConfigured exception if this setting is not set, or the workflow defined
            doesn't exist.
        '''
        workflow_code = getattr(settings, 'APPLICATION_WORKFLOW', None) 
        
        if workflow_code != None:
            try:
                approval_workflow = Workflow.objects.get(name=workflow_code)
                set_workflow(self, approval_workflow)
                
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('The workflow you specify in APPLICATION_WORKFLOW must actually be configured in the db')
                
        else:
            raise ImproperlyConfigured('You must set APPLICATION_WORKFLOW in the settings file')
    
    def _add_to_principle_investigator_role(self, the_user):
        '''
            Adds the user the principle investigator role that is defined in setting.PRINCIPLE_INVESTIGATOR_ROLE 
            (if this setting is not set, or the role doesn't exist then an ImproperlyConfigured exception will
            be raised). This will replace any other user that is already in this role.
        '''
        pass
        