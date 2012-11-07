from django.conf.urls import patterns, url



urlpatterns = patterns('review.views',
      url(r'^submit/(?P<ethics_application_id>\d+)/$',
          view ='submit_for_review', 
          name='submit_application'), 
                       
     url(r'^approve/(?P<ethics_application_id>\d+)/$',
          view ='evaluate_application_form', 
          name='configure_application_form',
        kwargs={'approved':True},),
                       
    url(r'^reject/(?P<ethics_application_id>\d+)/$',
          view ='evaluate_application_form', 
          name='configure_application_form',
        kwargs={'approved':False},),
       
)