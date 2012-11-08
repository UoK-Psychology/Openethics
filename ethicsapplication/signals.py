'''
Created on Nov 8, 2012

@author: jasonmarshall
'''
from django.dispatch.dispatcher import Signal


application_created= Signal(providing_args=['application'])