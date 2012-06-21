from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('basic.profiles.views',
    url(r'^edit/$',
        view='profile_edit',
        name='profile_edit',
    ),
    url(r'^(?P<username>[-\w]+)/$',
        view='profile_detail',
        name='profile_detail',
    ),
    url (r'^$',
         direct_to_template,
          { 'template': 'profile_index.html' }, 'profileindex'
         #view='profile_list',
         #name='profile_list',
    ),
)