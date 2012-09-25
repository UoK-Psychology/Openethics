from django.db import models
from django.contrib.auth.models import User



class CommitteeManager(models.Manager):
    '''
        The deafult manager for the Committee model
    '''
    
    def get_next_free_reviewer(self):
        '''
            This function should return the committe member who has the smallest
            application count. If there are two members with the same count then the
            user with the highest pk is returned. If there are no committee members
            then this function will return None
        
        '''
        return False
    
class Committee(models.Model):
    '''
        This model represents the review committee.
        It consists of a foreign key to users for the members
        of the committee, and a count which maintains the number of
        applications each committee member has reviewed.
    '''
    member = models.ForeignKey(User)
    count = models.IntegerField(max_length=3, default=0)

    objects = CommitteeManager()