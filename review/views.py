# Create your views here.
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def submit_for_review(request, ethics_application_id):
    '''
    
    '''
    
    return HttpResponseRedirect(reverse('index_view'))