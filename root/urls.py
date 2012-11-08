from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from root.api import UserResource
from ethicsapplication.api import EthicsApplicationResource
from tastypie.api import Api
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(EthicsApplicationResource())


urlpatterns = patterns('',
    
      url(r'^admin/', include(admin.site.urls)),#admin site
      url(r'^$', view='root.views.index_view', name='index_view'), #basic index page
      
      url(r'^accounts/login/$', view ='django.contrib.auth.views.login', name='auth_login'),
      url(r'^accounts/logout/$', view ='django.contrib.auth.views.logout', name='auth_logout'),
      
      # This is for overiding from outside apps   
      url(r'^application/', include('ethicsapplication.urls')),
      url(r'^checklist/', include('checklist.urls')),
      url(r'^applicationform/', include('applicationform.urls')),
      (r'^api/', include(v1_api.urls)),
      url(r'^review/', include('review.urls')),

)
