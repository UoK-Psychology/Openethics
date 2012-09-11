from django.conf.urls import patterns, url


urlpatterns = patterns('',
      url(r'^start/(?P<ethics_application_id>\d+)/$',
          view ='checklist.views.start_checklist', 
          name='start_checklist'), #start the checklist for a given ethics_application
      url(r'^do/(?P<questionnaire_id>\d+)/$',
          view ='questionnaire.views.do_questionnaire', 
          name='do_checklist',
          kwargs= {'template_name':'checklist/checklist_form.html',
                   'next_form_name':'handle_next_questiongroup_form',
                    'finished_url':'/'}),                  
     
)
