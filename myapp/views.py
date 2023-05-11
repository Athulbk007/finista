from django.shortcuts import render,redirect
from myapp.forms import SignUpForm,SignInForm,ProfileEditForm,PostForm,CoverPicForm,ProfilePicForm
from django.contrib.auth.models import User
from django.views.generic import CreateView,View,TemplateView,UpdateView,ListView,DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from myapp.models import UserProfile,Posts,Comments
from django.db.models import Q
from django.utils.decorators import method_decorator

# Create your views here.
#decorator
def signin_reqired(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"login plzz!!!!")
            return redirect("signin")
        return fn(request,*args,**kwargs)
    return wrapper
        


class SignUpView(CreateView):
    model=User
    template_name="register.html"
    form_class=SignUpForm
    success_url=reverse_lazy("signin")

    def form_valid(self, form):
        messages.success(self.request,"account has been created")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"failed to create account")
        return super().form_invalid(form)
    

class SignInView(View):
    model=User
    template_name="login.html"
    form_class=SignInForm

    def get(self,request,*args,**kwargs):
        form=self.form_class
        return render(request,self.template_name,{"form":form})
    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                
                return redirect("index")
        messages.error(request,"login failed")
        return render(request,self.template_name,{"form":form})
    
class ProfileEditView(UpdateView):
    model=UserProfile
    template_name="profileedit.html"
    form_class=ProfileEditForm
    success_url=reverse_lazy("index")

class IndexView(CreateView,ListView):
    template_name="index.html"
    model=Posts
    form_class=PostForm
    success_url=reverse_lazy("index")
    context_object_name="posts"
    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)
    
def signoutview(request,*args,**kwargs):
    logout(request)
    messages.success(request,"logout successfully")
    return redirect("signin")

def add_like_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect("index")

def add_commemt_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get("comment")
    User=request.user
    Comments.objects.create(user=request.user,post=post_obj,comment_text=comment)
    return redirect("index")

def comment_delete_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    comment_obj=Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect("index")
    else:
        messages.error(request,"plz contact admin")
        return redirect("signin")
    
class ProfileDetailView(DetailView):
    model=UserProfile
    template_name="profile.html"
    context_object_name="profile"

class Profile_listView(ListView):
    model=UserProfile
    template_name="profile-list.html"
    context_object_name="profiles" 
    #change query set
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)  

    def post(self,request,*args,**kwargs):
        pname=request.POST.get("username")
        qs=UserProfile.objects.filter(Q(user__username__icontains=pname) | Q(user__first_name__icontains=pname))
        return render(request,self.template_name,{"profiles":qs})
    

def chane_coverpic_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    form=CoverPicForm(instance=profile_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profiledetail",pk=id)
    return redirect("profiledetail",pk=id) 

def chane_profilepic_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    form=ProfilePicForm(instance=profile_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profiledetail",pk=id)
    return redirect("profiledetail",pk=id) 

def follow_View(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.add(profile_obj)
    user_prof.save()
    return redirect("index")


def unfollow_View(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.remove(profile_obj)
    user_prof.save()
    return redirect("index")

def post_delete_View(request,*args,**kwargs):
    post_id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=post_id)
    post_obj.delete()
    return redirect("index")