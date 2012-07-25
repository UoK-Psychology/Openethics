'''
Created on Jul 25, 2012

@author: jasonmarshall
'''
from django.forms import ModelForm
from Openethics.ethicsapplication.models import EthicsApplication


class EthicsApplicationForm(ModelForm):
    class Meta:
        model = EthicsApplication