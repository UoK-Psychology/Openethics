from django.conf.urls import patterns, url



urlpatterns = patterns('review.views',
      url(r'^submit/(?P<ethics_application_id>\d+)/$',
          view ='submit_for_review', 
          name='submit_application'), 
)