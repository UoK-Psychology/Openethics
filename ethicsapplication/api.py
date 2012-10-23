from tastypie.resources import ModelResource
from ethicsapplication.models import EthicsApplication
from tastypie import fields
from root.api import UserResource
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication

class EthicsApplicationResource(ModelResource):
    '''
        This is the API resource for the EthicsApplication model
    '''
    
    principle_investigator = fields.ForeignKey(UserResource, 'principle_investigator')#maps to the user resource defined in the root api
    
    class Meta:
        queryset = EthicsApplication.objects.all()
        resource_name = 'application'
        authentication = ApiKeyAuthentication()
        authorization= Authorization()
