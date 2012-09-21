from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
      url(r'^admin/', include(admin.site.urls)),#admin site
      url(r'^$', view='root.views.index_view', name='index_view'), #basic index page
      
      url(r'^accounts/login/$', view ='django.contrib.auth.views.login', name='auth_login'),
      url(r'^accounts/logout/$', view ='django.contrib.auth.views.logout', name='auth_logout'),
      
      # This is for overiding from outside apps   
      url(r'^application/', include('ethicsapplication.urls')),
      url(r'^checklist/', include('checklist.urls')),
      
      #temporarily put this here until we find a better place for it
      #url(r'questionnaire/', include('questionnaire.urls')),
      url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/(?P<group_limit>\d+)/$', 
          view = 'questionnaire.views.do_questionnaire',
          name = 'handle_next_questiongroup_form_single',
          kwargs={'template_name':'questionnaire/questionform.html',
                  'next_form_name':'handle_next_questiongroup_form',
                  'finished_url':'/questionnaire/finish/'},),
)
