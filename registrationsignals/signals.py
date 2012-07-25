from registration.signals import user_registered
from basic.profiles.models import Profile
    
def createProfile(sender, user, request, **kwargs):
    print "creating profile"
    Profile.objects.get_or_create(user=user)
        
     
#This is the signals that gets activated
#its imported from Python/Lib/site-packages/registration/signals.py
       
user_registered.connect(createProfile)