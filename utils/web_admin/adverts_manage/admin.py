from django.contrib import admin

from .models import Adverts


@admin.register(Adverts)
class AdvertsAdmin(admin.ModelAdmin):
    list_display = ("id",)
