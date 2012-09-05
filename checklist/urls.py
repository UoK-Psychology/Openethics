from django.conf.urls import patterns, url


urlpatterns = patterns('',
      url(r'^$',
          view ='', 
          name='do_checklist'), #do the checklist questionnaire for the first time
     
)
