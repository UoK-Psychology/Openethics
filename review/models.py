from django.db import models
from django.contrib.auth.models import User

class Committee(models.Model):
    '''
        This model represents the review committee.
        It consists of a foreign key to users for the members
        of the committee, and a count which maintains the number of
        applications each committee member has reviewed.
    '''
    member = models.ForeignKey(User)
    count = models.IntegerField(max_length=3)
