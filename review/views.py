# Create your views here.
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from permissions.utils import has_permission
from workflows.utils import do_transition
def submit_for_review(request, ethics_application_id):
    '''
    
    '''
    
    return HttpResponseRedirect(reverse('index_view'))