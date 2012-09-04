from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import AnswerSet
from django.db.models.manager import Manager
from workflows.utils import set_workflow
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from workflows.models import Workflow
from permissions.models import Role
from permissions.utils import remove_local_role, add_local_role
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
    
    __original_principle_investigator = None
    __original_id = None
    
    def __init__(self, *args, **kwargs):
        super(EthicsApplication, self).__init__(*args, **kwargs)
        
        #save the orginal values of the pi and the id so we can detect if they have changed without having to ask the db
        self.__original_principle_investigator = kwargs.get('principle_investigator', None)
        self.__original_id = self.id
        
        
    def save(self):
        
        super(EthicsApplication, self).save()
        
        if(self.__original_id != self.id): 
            #this is a new application that has been changed (or somehow the id has changed?!)
            self._add_to_workflow()
            self._add_to_principle_investigator_role()
            
            self.__original_id = self.id
            
        if(self.__original_principle_investigator != self.principle_investigator and self.__original_id == self.id ):#if pi has changed but id hasn't
            self._add_to_principle_investigator_role()
            
            self.__original_principle_investigator = self.principle_investigator
            
        
            
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
    
    def _add_to_principle_investigator_role(self):
        '''
            Adds the principle_investigator to the principle investigator role that is defined 
            in setting.PRINCIPLE_INVESTIGATOR_ROLE 
            (if this setting is not set, or the role doesn't exist then an ImproperlyConfigured exception will
            be raised). This will replace any other user that is already in this role.
        '''
        pi_code= getattr(settings, 'PRINCIPLE_INVESTIGATOR_ROLE', None)
        
        if pi_code != None:
            try:
                pi_role = Role.objects.get(name=pi_code)
                #check to see if the principle investigator is in the local for this role
                local_pi_users =  pi_role.get_local_users(self)
                if(not self.principle_investigator in local_pi_users):
                    #if not, remove all the local users from this role, and add the current principle investigator(there should only be one  user locally in theis role)
                    
                    for user in local_pi_users:
                        remove_local_role(self,user , pi_role)
                        
                    add_local_role(self, self.principle_investigator, pi_role)
                    
                    
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('The workflow you specify in PRINCIPLE_INVESTIGATOR_ROLE must actually be configured in the db')
        else:
            raise ImproperlyConfigured('You must set PRINCIPLE_INVESTIGATOR_ROLE in the settings file')
        