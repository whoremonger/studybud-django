from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from base.models import Room, User

class MyUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['name', 'username', 'email', 'password1', 'password2']

class RoomForm(ModelForm):
  class Meta:
    model = Room
    fields = '__all__' #based on all the fields in the Room model
    exclude = ['host', 'participants']
    
class UserForm(ModelForm):
  class Meta:
    model = User
    fields = ['avatar', 'name', 'username', 'email', 'bio']
     
