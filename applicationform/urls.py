from django.conf.urls import patterns, url


urlpatterns = patterns('',
      url(r'^group/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/$',
          view ='questionnaire.views.do_questionnaire', 
          name='do_application_form_group',
          kwargs={'template_name':'questionnaire/questionform.html',
                  'next_form_name':'handle_next_questiongroup_form',
                  'finished_url':'/questionnaire/finish/',
                  'group_limit':1},), 
                       
      url(r'^configure/(?P<ethics_application_id>\d+)/$',
          view ='applicationform.views.configure_application_form', 
          name='configure_application_form'),
       
)

