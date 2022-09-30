import asyncio

from ton import TonlibClient


async def main():
    ton_client = TonlibClient()
    ton_client.enable_unaudited_binaries()
    await ton_client.init_tonlib()

    # wallet = await ton_client.create_wallet()
    # print(wallet)
    # print(wallet.account_address)
    # print(wallet.account_address.account_address)
    #
    # seed = await wallet.export()
    # print(seed)

    seed = "amateur organ sustain betray leaf cram evil day huge dinner egg second captain jungle frozen matter theory tumble harsh tumble april rival humble outer"
    wallet = await ton_client.import_wallet(seed)
    print(wallet.account_address.account_address)
    print("EQB2rzwEHFTiYLcb7RusKOXCMNuoOZSm78uypEX-ivaSyz_F")


if __name__ == "__main__":
    asyncio.run(main())
