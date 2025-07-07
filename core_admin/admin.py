from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

class AdminPanelEntry:
    """empty object just to appear in admin pannel."""
    pass

@admin.register(AdminPanelEntry)
class AdminPanelEntryAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('msd-admin-action'))

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def get_model_perms(self, request):
        return {'change': True}  # for sidebar
