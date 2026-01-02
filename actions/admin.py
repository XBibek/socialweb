from django.contrib import admin
from .models import Action

# Register your models here.
@admin.register(Action)
class ActionADmin(admin.ModelAdmin):
    list_display = ['user', 'verb', 'target', 'get_total_likes', 'created']
    list_filter = ['created']
    search_fields = ['verb']

    @admin.display(description='Total Likes')
    def get_total_likes(self, obj):
        if obj.target and hasattr(obj.target, 'total_likes'):
            return obj.target.total_likes
        return '-'