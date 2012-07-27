# Create your views here.
from django.contrib.auth.decorators import login_required
from ethicsapplication.forms import EthicsApplicationForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse



@login_required
def create_application(request):
    
    '''
        This view function will be used to create a new ethics application.
        Login is required as the principle investigator for the new application
        will be set as the logged in user that is creating it.
        
        All valid users of the system should be able to create ethics applications.
    '''
    if request.method == 'POST':
        form  = EthicsApplicationForm(request.POST)
        
        if (form.is_valid()):
            
            new_application = form.instance
            
            new_application.principle_investigator = request.user
            new_application.save()
            
            return HttpResponseRedirect(reverse('application_view', kwargs={'application_id':new_application.id}))
            
    
    else:
        
        form = EthicsApplicationForm()
        
    return render_to_response('ethicsapplication/create.html', {'form':form},
                              context_instance=RequestContext(request))
    
def view_application(request, application_id):
    
    return HttpResponse('view application')
