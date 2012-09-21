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

    #application_view_url = reverse('application_view', kwargs={'application_id':ethics_application.id})
    #url = '%s?on_success=%s' % (base_url, application_view_url)

    application_success_url = reverse('configure_application_form', kwargs={'ethics_application_id':ethics_application.id})
    url = '%s?on_success=%s' % (base_url, application_success_url)

    return HttpResponseRedirect(url)
        
        

