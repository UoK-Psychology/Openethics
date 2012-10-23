'''
Created on 27 Jul 2012

@author: jjm20
'''
from django.contrib import admin
from ethicsapplication.models import EthicsApplication
from tastypie.models import ApiAccess,ApiKey

admin.site.register(EthicsApplication)
