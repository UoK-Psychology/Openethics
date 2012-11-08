from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ethicsapplication.models import EthicsApplication

def index_view(request):
    '''
        If there is a logged in user, we should find out if they have any active applications
        and put them in the context under the label: 'active_applications', otherwise we will 
        just render the index page wothout anything special in the context.
    
    '''
    
    context = {}
    
    if request.user.is_authenticated():
        #get their active applications
        context['active_applications'] = EthicsApplication.objects.get_applications_for_principle_investigator(request.user, 'with_researcher')
        context['applications_for_review'] = EthicsApplication.objects.get_applications_for_reviewer(request.user, 'awaiting_approval')
    return render_to_response('index.html', context,
                              context_instance=RequestContext(request))