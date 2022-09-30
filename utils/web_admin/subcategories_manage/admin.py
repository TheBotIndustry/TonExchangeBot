from django.contrib import admin

from .models import Subcategories


@admin.register(Subcategories)
class SubcategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "category_id", "name")
