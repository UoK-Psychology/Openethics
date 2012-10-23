from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = ApiKeyAuthentication()
        filtering = {'email': ALL}
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']