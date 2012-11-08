# Create your views here.
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from permissions.utils import has_permission
from workflows.utils import do_transition
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from ethicsapplication.models import EthicsApplication
from review.models import Committee
from django.contrib.auth.decorators import login_required
from review.signals import application_submitted_for_review,\
    application_accepted_by_reviewer, application_rejected_by_reviewer



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
    
    application_submitted_for_review.send(None, application=ethics_application, reviewer=reviewer)
    return HttpResponseRedirect(reverse('index_view'))


@login_required 
def evaluate_application_form(request, ethics_application_id, approved=False):
    '''
        This view will attempt to transition the ethics application to the 
        correct state depending on whether the approved flag is True, in which
        case it will have the Approved trnsition applied, otherwise it will have the 
        reject transition applied. All of this is dependent on the requesting user having
        the appropriate permissions to perform these transitions.
    '''
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    
    if approved:
        transition = 'approve'
        signal = application_accepted_by_reviewer
    else:
        transition = 'reject'
        signal = application_rejected_by_reviewer
    if not do_transition(ethics_application, transition, request.user):
        raise PermissionDenied()
    
    signal.send(None, application=ethics_application, reviewer=request.user)
    
    return HttpResponseRedirect(reverse('index_view'))






