from django.contrib import admin

from .models import Users


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("user_id", "full_name", "balance_toncoin", "freeze_balance_toncoin", "date_registration", "count_deals")
