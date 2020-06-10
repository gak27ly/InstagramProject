from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from Insta.models import Post

from django.contrib.auth.mixins import LoginRequiredMixin

from Insta.forms import CustomerUserCreationForm


class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsView(ListView):
    model = Post
    template_name = 'index.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    #all the model fileds are required
    fields = '__all__'
    login_url = 'login'

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    #no need to define fields, delete whole post
    #when delete use reverse_lazy
    success_url = reverse_lazy("posts")

class SignUp(CreateView):
    form_class = CustomerUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")
