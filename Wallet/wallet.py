# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI

from web3 import Web3

from eth_account import Account
 
 
# Create a function called `derive_wallets`
def derive_wallets(phrase, coin, numderive):
    command = f'php derive -g --mnemonic="{phrase}" --numderive={numderive} --coin={coin} --format=jsonpretty'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {'eth':derive_wallets(phrase=mnemonic,coin=ETH,numderive=3),'btc-test': derive_wallets(phrase=mnemonic,coin=BTCTEST,numderive=3)}
print(json.dumps(coins, indent=4, sort_keys=True))

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    global account
    if coin == 'eth':
        account=Account.privateKeyToAccount(priv_key)
    else:
        account=PrivateKeyTestnet(priv_key)
    return account

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin,account,recipient,amount):
    global tx_data
    if coin =='eth':
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        tx_data= {
            "from": account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
        }
        return tx_data
    else:
        tx_data = PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
        return tx_data

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == ETH:
        tx = create_tx(coin,account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        tx_data = create_tx(coin,account,recipient,amount)
        signed = account.sign_transaction(tx_data)
        NetworkAPI.broadcast_tx_testnet(signed)
        return signed