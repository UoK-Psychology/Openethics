from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from questionnaire.models import QuestionGroup, Questionnaire
from django.shortcuts import get_object_or_404
from ethicsapplication.models import EthicsApplication
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def start_checklist(request, ethics_application_id):
    '''
        This function is the gateway to completing the questionnaire. If required it will configure a 
        checklist questionnaire for the ethics application and then it will forward you to the appropraite
        view for completing the checklist form
    '''
    
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    
    if ethics_application.checklist == None:

        if not hasattr(settings, 'CHECKLIST_ID'):
            raise ImproperlyConfigured('Checklist ID not configured')
        else:
            try:
                checklist_group = QuestionGroup.objects.get(pk=settings.CHECKLIST_ID)
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('Checklist does not exist for configured id of: %s' % settings.CHECKLIST_ID)
    
        #configure the checklist questionnaire
        checklist_questionnaire = Questionnaire.objects.create(name='Checklist for application id: %s' % ethics_application.id)
        checklist_questionnaire.add_question_group(checklist_group)
        ethics_application.checklist = checklist_questionnaire
        ethics_application.save()
        
    base_url = reverse('do_checklist', kwargs={'questionnaire_id':ethics_application.checklist.id})
    application_success_url = reverse('finished_checklist', kwargs={'ethics_application_id':ethics_application.id})
    url = '%s?on_success=%s' % (base_url, application_success_url)

    return HttpResponseRedirect(url)
        
        
def finished_checklist(request, ethics_application_id):
    if not request.user.is_authenticated():
        raise PermissionDenied()
    
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    
    if not hasattr(settings, 'BASIC_APPLICATION_GROUPS'):
            raise ImproperlyConfigured('BASIC_APPLICATION_GROUPS ID not configured')
    else:
        application_groups = []
        for primary_key in settings.BASIC_APPLICATION_GROUPS:
            try:
                group = QuestionGroup.objects.get(pk=primary_key)
                application_groups.append(group)
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('Question group does not exist for configured id of: %s' % primary_key)
    
    if ethics_application.application_form is None:
        application_form_questionnaire = Questionnaire.objects.create(name='Application form for application id: %s' % ethics_application.id)
        for group in application_groups:
            application_form_questionnaire.add_question_group(group)
        
        ethics_application.application_form = application_form_questionnaire
        ethics_application.save()
           
    return HttpResponseRedirect(reverse('application_view', kwargs={'application_id':ethics_application_id}))



