import datetime

from utils.database_api.commands.deal import DB_Deal
from utils.database_api.models.users import Users


class DB_Users:
    async def add_user(self, user_id, full_name):
        new_user = Users()
        new_user.user_id = int(user_id)
        new_user.full_name = str(full_name)
        new_user.balance_toncoin = 0
        new_user.freeze_balance_toncoin = 0
        new_user.date_registration = datetime.datetime.utcnow()
        new_user.count_deals = 0
        await new_user.create()

    async def get_user(self, user_id) -> Users:
        return await Users.query.where(Users.user_id == int(user_id)).gino.first()

    async def get_balance_user(self, user_id, cryptocurrency) -> float:
        user = await self.get_user(user_id)
        if cryptocurrency == "TON":
            return user.balance_toncoin

    async def run_deposit(self, deal_id, user_id, cryptocurrency, amount):
        user = await self.get_user(user_id)
        if cryptocurrency == "TON":
            await user.update(balance_toncoin=user.balance_toncoin - amount, freeze_balance_toncoin=user.freeze_balance_toncoin + amount).apply()
        deal = await DB_Deal().get_deal(deal_id)
        await deal.update(is_deposit_for_sell=True).apply()

    async def get_back_deposit(self, user_id, cryptocurrency, amount):
        user = await self.get_user(user_id)
        if cryptocurrency == "TON":
            await user.update(balance_toncoin=user.balance_toncoin + amount, freeze_balance_toncoin=user.freeze_balance_toncoin - amount).apply()
