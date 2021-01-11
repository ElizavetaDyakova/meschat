from django.conf.urls import url
from advito import views
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from advito.views import SignupView, LoginView, EditProfileView, ProfileView, logout_view, PeopleView, EditPostView, DeletePostView
from django.contrib.auth.decorators import login_required



urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    path('all/', views.AllView.as_view(), name='all'),
    path('category/', views.category, name='category'),
    path('post/create/', views.CreatePostView.as_view(), name='post_create'),
    path('post/<int:add_id>/', views.PostView.as_view(), name='post_detail'),
    path('post/<int:add_id>/edit/', views.EditPostView.as_view(), name='post_edit'),
    path('post/<int:add_id>/delete/', views.DeletePostView.as_view(), name='post_delete'),
    path('people/', views.PeopleView.as_view(), name='people'),
    path('category/<int:category_id>/', views.cat_ord, name='categ'),
    path('category/create/', views.categ_create, name='categ_create'),
    path('<int:user_id>/profile/', ProfileView.as_view(), name='profile'),
    path('post/<int:add_id>/delete_success/', TemplateView.as_view(template_name='advito/delete_succes.html'), name='delete-post-success'),

]


from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns += [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('<int:user_id>/profile/edit', login_required(EditProfileView.as_view()), name='edit-profile'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('password_reset/', PasswordResetView.as_view(success_url=reverse_lazy('users:password_reset_done'),
                                                      template_name='my_auth/password_reset.html'),
         name='password_reset'),

    path('password_reset/done', PasswordResetDoneView.as_view(template_name='my_auth/password_reset_done.html'),
         name='password_reset_done'),

    path('password_reset/<str:uidb64>/<slug:token>', PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),

    path('password_reset/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]