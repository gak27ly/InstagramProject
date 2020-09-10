from annoying.decorators import ajax_request
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from Insta.models import Post, Like, InstaUser, Comment, UserConnection

from django.contrib.auth.mixins import LoginRequiredMixin

from Insta.forms import CustomerUserCreationForm


class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsView(ListView):
    model = Post
    template_name = 'index.html'
    login_url = "login"


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

class UserDetailView(DetailView):
    model = InstaUser
    template_name = 'user_detail.html'
    login_url = 'login'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    #all the model fileds are required
    fields = '__all__'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']
    login_url = 'login'

    def get_queryset(self):
        """ Limit a User to only modifying their own data. """
        qs = super(PostUpdateView, self).get_queryset()
        return qs.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    #no need to define fields, delete whole post
    #when delete use reverse_lazy
    success_url = reverse_lazy("posts")
    login_url = 'login'

class SignUp(CreateView):
    form_class = CustomerUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")

class FollowersView(ListView):
    model = InstaUser
    template_name = 'followers.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return 

        current_user = self.kwargs['pk']
        following = set()
        for conn in UserConnection.objects.filter(following=current_user).select_related('creator'):
            following.add(conn.creator)
        return InstaUser.objects.filter(username__in=following)

class FollowingsView(ListView):
    model = InstaUser
    template_name = 'followings.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return 

        current_user = self.kwargs['pk']
        following = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            following.add(conn.following)
        return InstaUser.objects.filter(username__in=following)


@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user,
                                            following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator=current_user,
                                              following=follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }
    
@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {'result': result, 'post_pk': post_pk}

@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username

        commenter_info = {'username': username, 'comment_text': comment_text}

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }

