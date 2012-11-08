from django.shortcuts import get_object_or_404, render_to_response
from ethicsapplication.models import EthicsApplication
from django.core.exceptions import PermissionDenied, ImproperlyConfigured,\
    ObjectDoesNotExist
from django.conf import settings
from questionnaire.models import QuestionGroup, Questionnaire, AnswerSet
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from applicationform.models import FullApplicationChecklistLink
from django.contrib.auth.decorators import login_required
from permissions.utils import has_permission
from django.template.context import RequestContext

def _get_application_groups_from_checklist(ethics_application):
    '''
        This function will interogate the results of the ethics_application checklist
        for every question that is answered yes|true then using then the appropriate 
        questiongroups will be added to a list of groups that should be included in the
        full application.
        If the checklist has not been completed then this function will raise an Attribute Error
        as the checklist is essential to this operation
    '''
    
    if ethics_application.checklist == None or not ethics_application.checklist.get_ordered_groups()[0] in ethics_application.get_answersets():
        raise AttributeError
    
    checklist_answer_set = ethics_application.get_answersets()[ethics_application.checklist.get_ordered_groups()[0]]
    
    all_groups = []
    for question_answer in checklist_answer_set.get_latest_question_answer_in_order():
        if bool(int(question_answer.answer)):
            
            all_groups += FullApplicationChecklistLink.objects.get_ordered_groups_for_question(question_answer.question)
            
    duplicates_removed = []
    [duplicates_removed.append(i) for i in all_groups if not duplicates_removed.count(i)]
    
    
    return duplicates_removed
    
    
    
def _get_basic_application_groups():
    '''
        This function returns a list of groups that are configured in the settings.BASIC_APPLICATION_GROUPS
        setting. It will raise an ImproperlyConfigured error if this setting is not present, or the groups
        it references don't exist.
    '''
    application_groups = []
    if not hasattr(settings, 'BASIC_APPLICATION_GROUPS'):
            raise ImproperlyConfigured('BASIC_APPLICATION_GROUPS ID not configured')
    else:
        for primary_key in settings.BASIC_APPLICATION_GROUPS:
            try:
                group = QuestionGroup.objects.get(pk=primary_key)
                application_groups.append(group)
            except ObjectDoesNotExist:
                raise ImproperlyConfigured('Question group does not exist for configured id of: %s' % primary_key)
    return application_groups   


def configure_application_form(request, ethics_application_id):
    '''
        Configures an application form for an EthicsApplication object.
        If the checlist is not completed on the Ethics Application then a 404 exception is thrown as 
        the checklist must be completed before the application can be generated.
    '''
    
    if not request.user.is_authenticated():
        raise PermissionDenied()
    
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    
    if ethics_application.checklist == None or not ethics_application.checklist.get_ordered_groups()[0] in ethics_application.get_answersets():
        raise Http404('Checklist answers do not exist')
    
    if ethics_application.application_form is None:
        
        basic_groups = _get_basic_application_groups()
        additional_groups = _get_application_groups_from_checklist(ethics_application)
        
        all_groups = basic_groups + additional_groups
        application_form_questionnaire = Questionnaire.objects.create(name='Application form for application id: %s' % ethics_application.id)
        
        for group in all_groups:
            application_form_questionnaire.add_question_group(group)
        
        ethics_application.application_form = application_form_questionnaire
        ethics_application.save()
           
    return HttpResponseRedirect(reverse('application_view', kwargs={'application_id':ethics_application_id}))


@login_required
def read_application_section(request, ethics_application_id, questionnaire_id, order_index, return_url):
    '''
        This function should first check that the user has view permission for the 
        application in question
        Then it should get the AnswerSet for the questiongroup as answered by the principle investigator
        of the application (the question group is referenced by the questionnaire_id and the order_index)
    '''
    if request.GET.get('return_url', None) != None:
        return_url = request.GET.get('return_url')
        
    ethics_application = get_object_or_404(EthicsApplication, pk=ethics_application_id)
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    
    try:
        ordered_groups = questionnaire.get_ordered_groups()
        question_group = ordered_groups[int(order_index)]
    except IndexError:
        raise Http404("Invalid order index")
    
    if not has_permission(ethics_application, request.user, 'view'):
        raise PermissionDenied()
    
    try:
        answer_set = AnswerSet.objects.get(user=ethics_application.principle_investigator,
                                           questionnaire=questionnaire,
                                           questiongroup=question_group)
        
        question_answers = answer_set.get_latest_question_answer_in_order()
        
    except ObjectDoesNotExist:
        #not to worry just return an empty list
        question_answers=[]
    
    return render_to_response('ethicsapplication/read_application_form.html', 
                              {     'return_url':return_url, 
                                    'question_answers':question_answers},
                              context_instance=RequestContext(request))
