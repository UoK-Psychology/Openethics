from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import AnswerSet, Questionnaire
from django.db.models.manager import Manager
from workflows.utils import set_workflow
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from workflows.models import Workflow
from permissions.models import Role
from permissions.utils import remove_local_role, add_local_role, get_object_for_principle_as_role
from workflows.utils import get_state

# Create your models here.

class EthicsApplicationManager(Manager):
    
    def get_active_applications(self, the_user):
        '''
            Returns the active applications for a user, will return an empty list if there
            aren't any active users.
        
        '''
        
        return [x for x in super(EthicsApplicationManager, self).get_query_set().filter(principle_investigator=the_user).filter(active=True)]
    
    def get_applications_for_review(self, reviewer):
        '''
            Returns the applications that the user is a reviewer for
            
            @param reviewer: The user object for the reviewer.
        '''
        
        return []

class EthicsApplication(models.Model):
    '''
        This defines an ethics application, it is the root model object
        from which all other information about the application can be found.
        It is thisobject that will be manipulated by the workflow engine.   
    '''
    
    title = models.CharField(max_length=255, default=None)  #default=None stops null strings which effectively makes it mandatory
    principle_investigator = models.ForeignKey(User ,related_name='pi')
    application_form = models.ForeignKey(Questionnaire, related_name='application_form', blank=True, null=True)
    active = models.BooleanField(default=True)
    checklist = models.ForeignKey(Questionnaire, related_name='checklist_questionnaire', blank=True, null=True)
    #TODO test the new checklist attribute
    objects = EthicsApplicationManager()
    
    __original_principle_investigator = None
    __original_id = None
    
    def __init__(self, *args, **kwargs):
        super(EthicsApplication, self).__init__(*args, **kwargs)
        
        #save the orginal values of the pi and the id so we can detect if they have changed without having to ask the db
        self.__original_principle_investigator = kwargs.get('principle_investigator', None)
        self.__original_id = self.id
        
    def save(self, force_insert=False, force_update=False, using=None):
        super(EthicsApplication, self).save(force_insert, force_update, using) 
        
        if(self.__original_id != self.id): 
            #this is a new application that has been changed (or somehow the id has changed?!)
            self._add_to_workflow()
            self._add_to_principle_investigator_role()
            
            self.__original_id = self.id
            
        if(self.__original_principle_investigator != self.principle_investigator and self.__original_id == self.id ):#if pi has changed but id hasn't
            self._add_to_principle_investigator_role()
            
            self.__original_principle_investigator = self.principle_investigator
            
        
            
    def __unicode__(self):
        return '%s, PI:%s' % (self.title, self.principle_investigator.username) # pragma: no cover
    


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
        
    def _get_answersets_for_questionnaire(self, questionnaire):
        
        answersets = {}
        
        if questionnaire != None:
            for group in questionnaire.get_ordered_groups():
                    try:
                        answer_set = AnswerSet.objects.get(user=self.principle_investigator,
                                                              questionnaire=questionnaire,
                                                              questiongroup=group)
                        answersets[group] = answer_set
                        
                    except ObjectDoesNotExist:
                        pass
                
        return answersets
    def get_answersets(self):
        '''
            Returns a dictionary that has questiongroups as the key and answersets as the values
            The questiongroups are those defined in the checklist and application_form questionnaires
            and the answersets are the answers for those questionnaires created by the principle investigator
        '''
        #for checklist
        answersets = {}
        if self.checklist != None:
            answersets.update(self._get_answersets_for_questionnaire(self.checklist))
        if self.application_form != None:
            answersets.update( self._get_answersets_for_questionnaire(self.application_form))
            
        return answersets
        
    def is_ready_to_submit(self):
        '''
            This function checks that both the checklist and the application for questionnaires are
            both complete. If they are it will return True, otherwise it will return False.
        '''
        answersets = self.get_answersets()
        
        if self.checklist == None or self.application_form == None:
            return False
        
        for group in self.checklist.get_ordered_groups() + self.application_form.get_ordered_groups():
            if group not in answersets or not answersets[group].is_complete():
                return False
            
        return True
    
    def get_current_state(self):
        '''
            This function returns the current state for this application. This will be useful to easily get the 
            state of a given application in a template
        '''
        return get_state(self)
    
    def assign_reviewer(self, user):
        '''
            This function assigns user to the reviewer role for this application
        '''
        if user is None or not isinstance(user, User):
            raise AttributeError('User specified was invalid')
        
        reviewer_code= getattr(settings, 'REVIEWER_ROLE', None)
        
        if reviewer_code != None:
            try:
                reviewer_role = Role.objects.get(name=reviewer_code)
                #check to see if the principle investigator is in the local for this role
                
                add_local_role(self, user, reviewer_role)
                    
                    
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('The workflow you specify in REVIEWER_ROLE must actually be configured in the db')
        else:
            raise ImproperlyConfigured('You must set REVIEWER_ROLE in the settings file')
        
        
        