'''
Created on Nov 8, 2012

@author: jasonmarshall
'''
from django.dispatch.dispatcher import Signal

application_submitted_for_review = Signal(providing_args=['application', 'reviewer'])
application_rejected_by_reviewer = Signal(providing_args=['application', 'reviewer'])
application_accepted_by_reviewer = Signal(providing_args=['application', 'reviewer'])