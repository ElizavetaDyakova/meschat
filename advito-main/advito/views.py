from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .exceptions import PermissionDenied
from .forms import PostForm, CatForm, CommentForm, SignupForm, LoginForm, UpdateProfileForm
from advito.models import Add, Category, Comment, Profile


class IndexView(ListView):
    '''
    вьюха для главной страницы
    '''
    model = Add
    template_name = 'advito/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Add.objects.order_by('-date_pub')[:6]


class AllView(ListView):
    '''
    вьюха для страницы всех объявлений
    '''
    model = Add
    template_name = 'advito/all.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Add.objects.order_by('-date_pub')


class PostView(DetailView):
    '''
    вьюха для просмотра поста
    '''
    model = Add
    context_object_name = 'post'
    comment_form = CommentForm
    pk_url_kwarg = 'add_id'
    template_name = 'advito/post-detail.html'

    def get(self, request, add_id, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['comments'] = Comment.objects.filter(in_post__id=add_id).order_by('-date_publish')
        context['comment_form'] = None
        if request.user.is_authenticated:
            context['comment_form'] = self.comment_form
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, add_id, *args, **kwargs):
        post = get_object_or_404(Add, id=add_id)
        form = self.comment_form(request.POST)
        if form.is_valid():
            comment = form.save()
            comment.author = request.user
            comment.in_post = post
            comment.save()
            comments = post.comment_set.all()
            return render(request, self.template_name, context={
                'comment_form': self.comment_form,
                'post': post,
                'comments': comments.order_by('-date_publish')
            })
        else:
            return render(request, self.template_name, context={
                'comment_form': form,
                'post': post,
                'comments': comments.order_by('-date_publish')
            })


def cat_ord(request, category_id):
    '''
    вьюха для просмотра постов по категориям
    '''
    category = get_object_or_404(Category, id=category_id)
    posts = Add.objects.filter(category=category)
    context = {
        'posts': posts,
    }
    return render(request, 'advito/cat_ord.html', context)



class PeopleView(ListView):
    '''
    вьюха для главной страницы
    '''
    model = Profile
    template_name = 'advito/people.html'
    context_object_name = 'users'

    def get_queryset(self):
        return Profile.objects.all()


class CreatePostView(CreateView):
    '''
    вьха для создания поста
    '''
    form_class = PostForm
    template_name = 'advito/post_create.html'

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        context = {}

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            context['post_was_created'] = True
            context['form'] = self.form_class
            return render(request, self.template_name, context)
        else:
            context['post_was_created'] = False
            context['form'] = form
            return render(request, self.template_name, context)


class DeletePostView(DeleteView):
    '''
    вьюха для удаления поста
    '''
    model = Add
    context_object_name = 'post'
    pk_url_kwarg = 'add_id'
    template_name = 'advito/post_delete.html'

    def get_success_url(self):
        add_id = self.kwargs['add_id']
        return reverse('delete-post-success', args=(add_id, ))


def category(request):
    '''
    вьюха для категорий
    '''
    categ_queryset = Category.objects.all()
    template = loader.get_template('advito/cat.html')
    context = {
        'categ': categ_queryset,
    }
    return HttpResponse(template.render(context))


class EditPostView(UpdateView):
    model = Add
    pk_url_kwarg = 'add_id'
    template_name = 'advito/post_edit.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise PermissionDenied("You are not author of this post")
        return super(EditPostView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        add_id = self.kwargs['add_id']
        return reverse('advito:post_detail', args=(add_id, ))


def categ_create(request):
    '''
    вьюха для создания объявления
    '''
    form_cat = CatForm()
    template_name = 'advito/cat_create.html'
    context = {'form_cat': form_cat}
    if request.method == "GET":
        return render(request, template_name, context)
    elif request.method == "POST":
        form_cat = CatForm(request.POST)

        if form_cat.is_valid():
            cat = form_cat.save(commit=False)
            cat.author = request.user
            cat.save()
            context['cat_was_created'] = True
            return render(request, template_name, context)
        else:
            context['cat_was_created'] = False
            context['form_cat'] = form_cat
            return render(request, template_name, context)

    return render(request, 'advito/cat_create.html', {'form_cat': form_cat})


from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout


class LoginView(LoginView):
    template_name = 'my_auth/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'), request)
            else:
                context = {}
                context['form'] = form
                return render(request=request, template_name=self.template_name, context=context)
        else:
            context = {'form': form}
            return render(request=request, template_name=self.template_name, context=context)


class ProfileView(DetailView):
    model = Profile
    template_name = 'advito/profile.html'

    def get_object(self):
        return get_object_or_404(Profile, user__id=self.kwargs['user_id'])


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse("index"))


class SignupView(View):
    template_name = 'my_auth/signup.html'
    registration_form = SignupForm

    def get(self, request, *args, **kwargs):
        context = {'form': self.registration_form}
        return render(request=request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        user_form = SignupForm(data=request.POST)
        registered = False
        if user_form.is_valid():
            user = user_form.save(commit=True)
            user.email = user_form.cleaned_data['email']
            user.save()
            registered = True
            return render(request, 'my_auth/signup.html',
                          {'registered': registered})
        else:
            return render(request, 'my_auth/signup.html',
                          {'form': user_form,
                           'registered': registered})


class EditProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'advito/edit_profile.html'
    slug_field = "user_id"
    slug_url_kwarg = "user_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("It is not your profile!")
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse('profile', args=(user_id,))



