# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def create_application(request):
    
    '''
        This view function will be used to create a new ethics application.
        Login is required as the principle investigator for the new application
        will be set as the logged in user that is creating it.
        
        All valid users of the system should be able to create ethics applications.
    '''
    return HttpResponse('create_application')