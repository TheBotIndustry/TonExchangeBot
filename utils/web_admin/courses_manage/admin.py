from django.contrib import admin

from .models import Courses


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "course_rub")
