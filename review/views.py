# Create your views here.
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from permissions.utils import has_permission
from workflows.utils import do_transition
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from ethicsapplication.models import EthicsApplication
from review.models import Committee



def submit_for_review(request, ethics_application_id):
    '''
        This view will ascertain if the submit_for_review transition can be
        carried out on the specified ethicsApplication, by the logged in user.
        If any of the following goes wrong then a forbidden exception will be raised:
        1.User is not logged in
        2.User does not have the submit permission for this application
        3.The transition is not allowed
    '''
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    
    if not request.user.is_authenticated() or not has_permission(ethics_application, request.user, 'submit') or not do_transition(ethics_application, 'submit_for_review', request.user):
        raise PermissionDenied()
    
    reviewer = Committee.objects.get_next_free_reviewer()
    ethics_application.assign_reviewer(reviewer)
    
    return HttpResponseRedirect(reverse('index_view'))