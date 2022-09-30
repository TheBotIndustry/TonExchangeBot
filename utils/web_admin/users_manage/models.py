from django.db import models


class Users(models.Model):
    class Meta:
        db_table = "users"
        verbose_name = "👤 Пользователь"
        verbose_name_plural = "👥 Пользователи"

    user_id = models.BigIntegerField(verbose_name="Telegram ID", primary_key=True)
    full_name = models.TextField(verbose_name="Имя", null=True, blank=True)
    balance_toncoin = models.FloatField(verbose_name="Баланс Toncoin")
    freeze_balance_toncoin = models.FloatField(verbose_name="Замороженный баланс Toncoin")
    date_registration = models.DateTimeField(verbose_name="Дата регистрации")
    count_deals = models.IntegerField(verbose_name="Количество сделок")

    def __str__(self):
        return f"{self.user_id}"
