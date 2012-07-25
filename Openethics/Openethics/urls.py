from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
      url(r'^admin/', include(admin.site.urls)),#admin site
      (r'^$', direct_to_template, { 'template': 'index.html' }, 'index'), #basic index page
      
      # This is for overiding from outside apps   
      (r'^accounts/', include('registration.backends.default.urls')),# This url redirect to registration default backend  
      (r'^accounts/profile/', include('Openethics.profiles.urls')),# This url redirect to our custom profile urls
      (r'^application/', include('ethicsapplication.urls')),








)
