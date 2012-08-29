from django.http import HttpResponse


def index_view(request):
    '''
        If there is a logged in user, we should find out if they have any active applications
        and put them in the context under the label: 'active_applications', otherwise we will 
        just render the index page wothout anything special in the context.
    
    '''
    
    
    return HttpResponse('indexio')