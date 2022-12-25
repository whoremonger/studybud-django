from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from base.models import Room, Topic, Message, User
from django.contrib.auth import authenticate, login, logout 
from django.db.models import Q
from base.forms import RoomForm, UserForm, MyUserCreationForm
#make sure the app templates have a folder in there with the same name as the app like base/template -> base folder

#rooms = [
  #{ 'id': 1, 'name': 'Lets learn python!' },
  #{ 'id': 2, 'name': 'Design with me' },
  #{ 'id': 3, 'name': 'Frontend developers' },
#]

def loginPage(request): #do not call the function login there is a function already named
  page = 'login'
  if request.user.is_authenticated: #to hide the login link from the logged in user
    return redirect('home')
  
  if request.method == 'POST':
    email = request.POST.get('email').lower()
    password = request.POST.get('password')
    try:
      user = User.objects.get(email=email)
    except:
      messages.error(request, 'User does not exist.')
      
    user = authenticate(request, email=email, password=password)
    
    if user is not None:
      login(request, user) #creates a session in database and browser
      return redirect('home')
    else: 
      messages.error(request, 'Username OR Password does not exist.')
      
  context = {'page': page}
  return render(request, 'base/login_register.html', context)

def logoutUser(request):
  logout(request)
  return redirect('home') 

def registerPage(request):
  form = MyUserCreationForm()
  
  if request.method == 'POST':
    form = MyUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False) #makes it so you can clean the data later
      user.username = user.username.lower()
      user.save()
      login(request, user) #after registering logs him in
      return redirect('home')
    else:
      messages.error(request, 'An error occurred during registration.')

  return render(request, 'base/login_register.html', {'form': form})

def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)) 
  #when a url query contains a few letters it will automatically match the topic #Q is a django function for the model
  #makes it so that all that search parameters doesn't all need to in one search but is separate with ORs
  
  topics = Topic.objects.all()[0:5] #how to change how much to display on screen at a time
  room_count = rooms.count() #built in method
  room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
  
  #another reason to use context dictionary is to use components so it can read the data as long as components are used in the same page
  context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages} # a variable to make it easier to handle the dictionary
  return render(request, 'base/home.html', context)

def room(request, pk): #to add to add the parameter string
  room = Room.objects.get(id=pk)
  room_messages = room.message_set.all() #A relationship, #messages are a child of room and the messages are the comments 'give us the messages_set (lowercase) related to this specific room'
  participants = room.participants.all()
  
  
  if request.method == "POST":
    message = Message.objects.create(
      user = request.user,
      room = room,
      body = request.POST.get('body')
    )
    room.participants.add(request.user)
    return redirect('room', pk=room.id)
  
  context = {'room': room, 'room_messages': room_messages, 'participants': participants}
  return render(request, 'base/room.html', context) 

def userProfile(request, pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all() #getting all the children in room with room_set.all() 
  room_messages = user.message_set.all()
  topics = Topic.objects.all()
  context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
  return render(request, 'base/profile.html', context)

@login_required(login_url='login')  #a decorator to restrict user to login
def createRoom(request): #data comes through request
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name) #if it cant find it, it will create it
    Room.objects.create(
      host=request.user,
      topic=topic,
      name=request.POST.get('name'),
      description=request.POST.get('description'),
    )
    return redirect('home') #can access site from the name
  
  context = {'form': form, 'topics': topics}
  return render(request, 'base/room_form.html', context) 

@login_required(login_url='login') 
def updateRoom(request, pk): 
  room = Room.objects.get(id=pk)
  form = RoomForm(instance=room)
  topics = Topic.objects.all()
  if request.user != room.host:
    return HttpResponse('You\'re not allowed here!!')
  
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('home')
  context = {'form': form, 'topic': topics, 'room': room}
  return render(request, 'base/room_form.html', context)

@login_required(login_url='login') 
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)
  
  if request.user != room.host:
    return HttpResponse('You\'re not allowed here!!')
  
  if request.method == 'POST':
    room.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login') 
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)
  
  if request.user != message.user:
    return HttpResponse('You\'re not allowed here!!')
  
  if request.method == 'POST':
    message.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login') 
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)
  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', pk=user.id)
  return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  topics = Topic.objects.filter(name__icontains=q)
  return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
  room_messages = Message.objects.all()
  return render(request, 'base/activity.html', {'room_messages': room_messages})

#finished but need to fix the register user error. Its not logging in. Its not accepting the passwords.












  
