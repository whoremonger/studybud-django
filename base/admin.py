from django.contrib import admin

# Register your models here.

#Need to add models on here so the built in django admin table can use it

from base.models import Room, Topic, Message, User

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)






