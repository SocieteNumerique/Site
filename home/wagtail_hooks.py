from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)
from .models import ForWhatTag, ForWhoTag


class ForWhoTagsModelAdmin(ModelAdmin):
    model = ForWhoTag
    menu_label = 'Tags "Pour qui?"'
    menu_icon = "group"
    form_fields_exclude = ("slug",)
    add_to_settings_menu = True
    list_display = ["name"]
    search_fields = ("name",)


class ForWhatTagsModelAdmin(ModelAdmin):
    model = ForWhatTag
    menu_label = 'Tags "Pour quoi?"'
    menu_icon = "list-ul"
    form_fields_exclude = ("slug",)
    add_to_settings_menu = True
    list_display = ["name"]
    search_fields = ("name",)


class MyModelAdminGroup(ModelAdminGroup):
    menu_label = "Mes tags"
    menu_icon = "tag"
    menu_order = 200  # will put in 4th place (000 being 1st, 100 2nd)
    items = (ForWhoTagsModelAdmin, ForWhatTagsModelAdmin)


modeladmin_register(MyModelAdminGroup)
