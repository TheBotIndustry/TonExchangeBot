from django.db import models


class Adverts(models.Model):
    class Meta:
        db_table = "adverts"
        verbose_name = "Объявление"
        verbose_name_plural = "Список объявлений"

    id = models.AutoField(verbose_name="ID", primary_key=True)
    user_id = models.BigIntegerField(verbose_name="Telegram ID")
    cryptocurrency = models.TextField(verbose_name="Криптовалюта")
    is_sell = models.BooleanField(verbose_name="Продажа?")
    currency = models.TextField(verbose_name="Валюта")
    category_id = models.IntegerField(verbose_name="ID категории")
    subCategory_id = models.IntegerField(verbose_name="ID подкатегории")
    fixPrice = models.FloatField(verbose_name="Фиксированная цена", null=True, blank=True)
    percent = models.FloatField(verbose_name="Проценты", null=True, blank=True)
    decimalPercent = models.TextField(verbose_name="Знак процентов", null=True, blank=True)
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    dateCreated = models.DateTimeField(verbose_name="Дата создания")
    limitLow = models.FloatField(verbose_name="Нижний лимит")
    limitHigh = models.FloatField(verbose_name="Верхний лимит")
    status = models.BooleanField(verbose_name="Статус", default=True)

    def __str__(self):
        return f"{self.id}"
