import datetime

from utils.database_api.models.deal import Deal
from utils.database_api.models.users import Users


class DB_Deal:
    async def add_deal(self, category_id, subcategory_id, advert_id, creator_user_id, user_id, is_sell, cryptocurrency, currency, amount_crypto,
                       amount_currency) -> Deal:
        new_deal = Deal()

        new_deal.advert_id = int(advert_id)
        new_deal.category_id = int(category_id)
        new_deal.subcategory_id = int(subcategory_id)
        new_deal.creator_user_id = int(creator_user_id)
        new_deal.user_id = int(user_id)
        new_deal.is_sell = is_sell
        if is_sell:
            user = await Users.query.where(Users.user_id == int(user_id)).gino.first()
            if cryptocurrency == "TON":
                await user.update(balance_toncoin=user.balance_toncoin - amount_crypto,
                                  freeze_balance_toncoin=user.freeze_balance_toncoin + amount_crypto).apply()
        new_deal.currency = currency
        new_deal.amount_crypto = amount_crypto
        new_deal.amount_currency = amount_currency
        new_deal.status_start = False
        new_deal.status_finish = False
        new_deal.status_arbitr = False
        new_deal.date_start = datetime.datetime.utcnow()

        await new_deal.create()
        return new_deal

    async def get_deal(self, deal_id) -> Deal:
        deal = await Deal.query.where(Deal.id == int(deal_id)).gino.first()
        return deal

    async def delete_deal(self, deal_id):
        deal = await self.get_deal(deal_id)
        await deal.delete()

    async def update_message_deal(self, deal_id, creator_mess_id=None, user_mess_id=None):
        deal = await self.get_deal(deal_id)
        if creator_mess_id:
            await deal.update(creator_mess_id=creator_mess_id).apply()
        if user_mess_id:
            await deal.update(user_mess_id=user_mess_id).apply()

    async def update_payment_deal(self, deal_id, payment):
        deal = await self.get_deal(deal_id)
        await deal.update(payment=payment).apply()

    async def start_deal(self, deal_id):
        deal = await self.get_deal(deal_id)
        await deal.update(status_start=True).apply()

    async def finish_deal(self, deal_id):
        deal = await self.get_deal(deal_id)
        creator = await Users.query.where(Users.user_id == deal.creator_user_id).gino.first()
        user = await Users.query.where(Users.user_id == deal.user_id).gino.first()

        await creator.update(count_deals=creator.count_deals + 1).apply()
        await user.update(count_deals=user.count_deals + 1).apply()
        if deal.is_sell:
            if deal.cryptocurrency == "TON":
                await creator.update(balance_toncoin=creator.balance_toncoin + deal.amount_crypto).apply()
                await user.update(freeze_balance_toncoin=user.freeze_balance_toncoin - deal.amount_crypto).apply()
        else:
            if deal.cryptocurrency == "TON":
                await user.update(balance_toncoin=user.balance_toncoin + deal.amount_crypto).apply()
                await creator.update(freeze_balance_toncoin=creator.freeze_balance_toncoin - deal.amount_crypto).apply()

        await deal.update(status_finish=True).apply()
