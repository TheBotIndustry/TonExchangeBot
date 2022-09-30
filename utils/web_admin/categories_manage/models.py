from django.db import models


class Categories(models.Model):
    class Meta:
        db_table = "categories"
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"

    id = models.AutoField(verbose_name="ID", primary_key=True)
    name = models.TextField(verbose_name="Название")
    currency = models.TextField(verbose_name="Валюта")

    def __str__(self):
        return f"{self.id}"
