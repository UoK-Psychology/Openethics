from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
      url(r'^admin/', include(admin.site.urls)),#admin site
      (r'^$', direct_to_template, { 'template': 'index.html' }, 'index'), #basic index page
      
      url(r'^accounts/login/$', view ='django.contrib.auth.views.login', name='auth_login'),
      url(r'^accounts/logout/$', view ='django.contrib.auth.views.logout', name='auth_logout'),
      
      # This is for overiding from outside apps   
      url(r'^application/', include('ethicsapplication.urls')),
)
