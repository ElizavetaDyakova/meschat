from django.contrib import admin
from .models import Profile, Add, Category, Comment


admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Comment)



from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)


class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['author', 'header', 'image']}),
        ('Detail information', {'fields': ['description', 'category']})
    ]
    readonly_fields = ['date_pub', 'date_edit']
    list_display = ('author', 'date_pub', 'date_edit')
    list_filter = ('date_pub', 'date_edit')
    search_fields = ['author', 'header']


class PostInline(admin.StackedInline):
    model = Add
    fields = ['author', 'header', 'description', 'category', 'image']
    readonly_fields = ['date_pub', 'date_edit']
    extra = 3


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [PostInline]

admin.site.register(Add, PostAdmin)