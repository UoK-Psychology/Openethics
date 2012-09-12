
from django import template
from permissions.utils import has_permission
from workflows.utils import get_allowed_transitions
register = template.Library()

class HasPermissionForObjectNode(template.Node):
    
    
    @classmethod
    def handle_token(cls, parser, token):
        
        
        try:
            tag_name, object_under_test , permission = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % tag_name)
        
        
        end_tag = 'end_if_has_permission_for_object'
        
        nodelist_true = parser.parse(('else', end_tag)) # the part of the tag between start and else (or end if there isn't an else)
        
        token = parser.next_token() #parse the token 
        
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag,)) # the contents of the else block if there is one
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(object_under_test , permission, nodelist_true, nodelist_false)
    
    
    def __init__(self, object_under_test, permission_string, nodelist_true, nodelist_false):
        self.object_under_Test = template.Variable(object_under_test)
        self.permission_string = permission_string
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    
    def render(self, context):
        
        try: 
            object_under_Test = self.object_under_Test.resolve(context) #resolve the actual object from the context
            user = context.get("user")
            
            if has_permission(object_under_Test, user, self.permission_string):
                return self.nodelist_true.render(context)
            else:
                if isinstance(self.nodelist_false, str):
                    return self.nodelist_false
                else:
                    return self.nodelist_false.render(context)
                
            
        except template.VariableDoesNotExist:
            return ''
    
    
@register.tag(name='if_has_permission_for_object')
def do_has_permission_for_object(parser, token):
    return HasPermissionForObjectNode.handle_token(parser, token)


