from django.db import models


class Courses(models.Model):
    class Meta:
        db_table = "courses"
        verbose_name = "Курс"
        verbose_name_plural = "Курсы криптовалют/фиат"

    id = models.AutoField(verbose_name="ID", primary_key=True)
    name = models.TextField(verbose_name="Название")
    course = models.FloatField(verbose_name="Курс 1 монета к доллару")
    course_rub = models.FloatField(verbose_name="Курс 1 монета к рублю")

    def __str__(self):
        return f"{self.id}"
