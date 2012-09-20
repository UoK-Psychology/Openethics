from django.shortcuts import get_object_or_404
from ethicsapplication.models import EthicsApplication
from django.core.exceptions import PermissionDenied, ImproperlyConfigured,\
    ObjectDoesNotExist
from django.conf import settings
from questionnaire.models import QuestionGroup, Questionnaire
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def configure_application_form(request, ethics_application_id):
    '''
        Configures an application form for an EthicsApplication object.
    '''
    
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
