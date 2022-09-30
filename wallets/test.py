import base64
import os
import subprocess
from pathlib import Path

import crc16 as crc16
from toncli.modules.utils.fift.fift import fift_execute_command
from toncli.modules.utils.lite_client.commands import lite_client_execute_command
from toncli.modules.utils.lite_client.lite_client import LiteClient


def get_seqno(address: str):
    lite_client = LiteClient('runmethod', args=[address, 'seqno'],
                             kwargs={'lite_client_args': '-v 0',
                                     'net': 'mainnet',
                                     'update': False},
                             get_output=True)
    output = lite_client.run()
    output = str(output, "utf-8")
    output = output.split("\n")[-3]
    try:
        seqno = int(output.split("[ ")[-1].split(" ]")[0])
    except:
        seqno = 1
    return seqno


def create_account(user_id):
    path_to_contract = Path(__file__).parent.joinpath(
        "/home/job/Projects/toncoin_exchange/wallet/fift/new-wallet-v3.fif")
    command = fift_execute_command(str(path_to_contract),
                                   ["0", "111", f"/home/job/Projects/toncoin_exchange/wallets/{user_id}"])
    output = subprocess.check_output(command, cwd=os.getcwd())
    output_data = output.decode()
    address = output_data.split("new wallet address = ")[-1].split("(Saving address to file")[0]
    address = address.split(' \n')[0]
    buff = address.split(":")
    workchain = int(buff[0])
    addr_hex = buff[1]
    b = bytearray(36)
    b[0] = 0x51 - True * 0x40 + False * 0x80
    b[1] = workchain % 256
    b[2:34] = bytearray.fromhex(addr_hex)
    buff = bytes(b[:34])
    crc = crc16.crc16xmodem(buff)
    b[34] = crc >> 8
    b[35] = crc & 0xff
    address_b64 = base64.b64encode(b)
    address_b64 = address_b64.decode()
    address_b64 = address_b64.replace('+', '-')
    address_b64 = address_b64.replace('/', '_')
    return address_b64


def send_transfer(user_id, from_address, wallet_id, to_address, amount):
    seqno = get_seqno(from_address)
    path_to_contract = Path(__file__).parent.joinpath(
        "/home/job/Projects/toncoin_exchange/wallet/fift/wallet-v3.fif")
    command = fift_execute_command(str(path_to_contract),
                                   [f"/home/job/Projects/toncoin_exchange/wallets/{user_id}", str(to_address),
                                    str(wallet_id), str(seqno), str(amount), "--no-bounce",
                                    f"/home/job/Projects/toncoin_exchange/wallets/transfer-{user_id}"])
    subprocess.run(command, cwd=os.getcwd())

    new_command = lite_client_execute_command("mainnet", ['-v', '2', '-c',
                                                          f'sendfile /home/job/Projects/toncoin_exchange/wallets/transfer-{user_id}.boc'],
                                              update_config=False)
    subprocess.run(new_command, cwd=os.getcwd())
    os.remove(f"/home/job/Projects/toncoin_exchange/wallets/transfer-{user_id}.boc")


user_id = 621788239
to_address = "EQBJyPQUt87vAozSscZj-Qy4dsQAs9xiMUcwuPL5lsz6oVLr"

from_address = "EQB6L96Y-wUncOsIttEcfj3T6rp5w5da8NSTL-SoIambTQPL"  # 5

# send_transfer(user_id=621788239, from_address=to_address, wallet_id=111, to_address=from_address, amount=0.005)
# balance_status = get_account_status(network="mainnet", address=to_address)
# print(balance_status[0])

address = create_account(123456789)
print(address)

print(get_seqno("EQB6L96Y-wUncOsIttEcfj3T6rp5w5da8NSTL-SoIambTQPL"))
