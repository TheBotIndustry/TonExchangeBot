from django.db import models


class Subcategories(models.Model):
    class Meta:
        db_table = "subcategories"
        verbose_name = "Подкатегория"
        verbose_name_plural = "Список подкатегорий"

    id = models.AutoField(verbose_name="ID", primary_key=True)
    category_id = models.IntegerField(verbose_name="ID категории")
    name = models.TextField(verbose_name="Название")

    def __str__(self):
        return f"{self.id}"
