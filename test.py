import tonos_ts4.ts4 as ts4
import unittest
import time

ZERO_ADDRESS = "0:" + "0" * 64

class key:
    secret: str
    public: str
class TestPair(unittest.TestCase):
    secret = "bc891ad1f7dc0705db795a81761cf7ea0b74c9c2a93cbf9ac1bad8bd30c9b3b75a4889716084010dd2d013e48b366424c8ba9d391c867e46adce51b18718eb67"
    public = "0x5a4889716084010dd2d013e48b366424c8ba9d391c867e46adce51b18718eb67"
    def test_exchanger(self):
        ts4.reset_all() # reset all data
        ts4.init('True-NFT/components/true-nft-core/build/', verbose = True)
        key1 = ts4.make_keypair()
        self.public1 = key1[1]
        self.secret1 = key1[0]
        codeIndex = ts4.load_code_cell('Index.tvc')
        codeData = ts4.load_code_cell('Data.tvc')
        constructor = {
            "codeIndex":codeIndex,
            "codeData":codeData

        }
        main = ts4.BaseContract('NftRoot',constructor,initial_data=dict(_addrOwner=ts4.Address(ZERO_ADDRESS),_signs=[self.public]),pubkey=self.public1,private_key=self.secret1,balance=150_000_000_000,nickname="Controller0")
        ts4.dispatch_messages()
        main.call_method("mintNft",dict(metadata=ts4.Bytes("5423")),self.secret)
        ts4.dispatch_messages()
        num = main.call_getter("_totalMinted",dict())
        print(num)
        addr = main.call_getter("resolveData",dict(addrRoot=main.addr,id=num - 1,name=ts4.Bytes("5423")))
        nft_token = ts4.BaseContract('Data',dict(codeIndex=codeIndex,authority_signs=[str(int(self.public,16))]),address=addr)
        print(nft_token.call_getter("getInfo",dict()))
        print(nft_token.call_getter("_authority_signs",dict()))
        nft_token.call_method("addMessage", dict(amsg=ts4.Bytes("1010")), private_key=self.secret1,expect_ec=201)
        nft_token.call_method("addMessage", dict(amsg=ts4.Bytes("1010")), private_key=self.secret)
        ts4.dispatch_messages()
        print(nft_token.call_getter("getInfo",dict()))

if __name__ == '__main__':
    unittest.main()
