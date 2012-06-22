from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jmtest.views.home', name='home'),
    # url(r'^jmtest/', include('jmtest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
      url(r'^admin/', include(admin.site.urls)),
      
    # This is for overiding from outside apps  
      #url(r'^accounts/', include('Openethics.my_registration_urls')),
      
    # This url redirect to registration default backend    
      (r'^accounts/', include('registration.backends.default.urls')),
     # (r'^register/$', include('Openethics.account.views.AccountRegistration')),

    # This url redirect to profile default backend
      ('^accounts/profile/', include('basic.profiles.urls')),
      #  (r'^profiles/', include('profile.backends.simple.url')),
      # (r'^profile/', include('profile.urls')),


      (r'^$', direct_to_template,
          { 'template': 'index.html' }, 'index'),








)
