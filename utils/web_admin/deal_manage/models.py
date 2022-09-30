from django.db import models


class Deal(models.Model):
    class Meta:
        db_table = "deal"
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"

    id = models.AutoField(verbose_name="ID", primary_key=True)
    category_id = models.IntegerField(verbose_name="ID Категории")
    subcategory_id = models.IntegerField(verbose_name="ID Подкатегории")
    advert_id = models.IntegerField(verbose_name="ID Объявления")
    creator_user_id = models.BigIntegerField(verbose_name="User ID создателя объявления")
    creator_mess_id = models.IntegerField(verbose_name="Mess ID создателя объявления", null=True, blank=True)
    user_id = models.BigIntegerField(verbose_name="User ID создателя сделки")
    user_mess_id = models.IntegerField(verbose_name="Mess ID создателя сделки", null=True, blank=True)
    is_sell = models.BooleanField(verbose_name="Сделка по продаже?")
    is_deposit_for_sell = models.BooleanField(verbose_name="Был депозит со стороны продавца?", null=True, blank=True, default=False)
    cryptocurrency = models.TextField(verbose_name="Криптовалюта")
    currency = models.TextField(verbose_name="Валюта")
    amount_crypto = models.FloatField(verbose_name="Сумма сделки в крипте")
    amount_currency = models.FloatField(verbose_name="Сумма сделки в валюте")
    status_start = models.BooleanField(verbose_name="Сделка началась?")
    payment = models.TextField(verbose_name="Реквизиты", null=True, blank=True)
    status_finish = models.BooleanField(verbose_name="Сделка завершена?")
    status_arbitr = models.BooleanField(verbose_name="Сделка в арбитраже?")
    date_start = models.DateTimeField(verbose_name="Дата начала сделки")
    date_finish = models.DateTimeField(verbose_name="Дата завершения сделки", null=True, blank=True)

    def __str__(self):
        return f"{self.id}"
