
from tonclient.client import TonClient
import base64
import json
import time
from tonclient.errors import TonException
from tonclient.test.test_abi import SAMPLES_DIR
from tonclient.test.helpers import send_grams
from tonclient.types import Abi, DeploySet, CallSet, Signer, FunctionHeader, \
    ParamsOfEncodeMessage, ParamsOfProcessMessage, ProcessingResponseType, \
    ProcessingEvent, ParamsOfSendMessage, ParamsOfWaitForTransaction, ClientConfig, \
        BuilderOp, NetworkConfig, ParamsOfRunGet, ParamsOfQuery, ParamsOfGetCodeFromTvc, \
            ParamsOfRunTvm, AccountForExecutor, ParamsOfWaitForCollection, ParamsOfRunExecutor
import hashlib


class wrapper:
    def __init__(self, url="https://rfld-dapp01.ds1.itgold.io",giver_address="0:deda155da7c518f57cb664be70b9042ed54a92542769735dfb73d3eef85acdaf",real=False):
        self.client = TonClient(config=ClientConfig(network=NetworkConfig(server_address=url)))
        self.url = url
        self.giver_address = giver_address
        self.real = real

        self.main_abi = Abi.from_path(
            path='True-NFT/components/true-nft-core/build/NftRoot.abi.json')
        self.data_abi = Abi.from_path(
            path='True-NFT/components/true-nft-core/build/Data.abi.json')

        with open('True-NFT/components/true-nft-core/build/Index.tvc', 'rb') as fp:
            self.codeIndex = self.client.boc.get_code_from_tvc(
                params=ParamsOfGetCodeFromTvc(tvc=base64.b64encode(fp.read()).decode()))

        with open('True-NFT/components/true-nft-core/build/Data.tvc', 'rb') as fp:
            self.codeData = self.client.boc.get_code_from_tvc(
                params=ParamsOfGetCodeFromTvc(tvc=base64.b64encode(fp.read()).decode()))

        self.keypair = self.client.crypto.generate_random_sign_keys()
        # self.helper_abi = Abi.from_path(
        #     path='helper.abi.json')





    def send_grams(self, address: str):
        if self.real:
            input(f"Send some grams to: {address}")
        else:
            giver_abi = Abi.from_path(
                path='grant.abi.json')
            call_set = CallSet(
                function_name='grant', input={'addr': address})
            encode_params = ParamsOfEncodeMessage(
                abi=giver_abi, signer=Signer.NoSigner(), address=self.giver_address,
                call_set=call_set)
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            self.client.processing.process_message(params=process_params)

    def create_root(self,signs):
        with open('True-NFT/components/true-nft-core/build/NftRoot.tvc', 'rb') as fp:
            self.main_deploy_set = DeploySet(tvc=base64.b64encode(fp.read()).decode(),initial_data=dict(_addrOwner="0:" + "0" * 64,_signs=signs))
            self.main_boc = base64.b64encode(fp.read()).decode()
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(pubkey=self.keypair.public),input=dict(codeIndex=self.codeIndex.code,codeData=self.codeData.code))
        encode_params = ParamsOfEncodeMessage(
                    abi=self.main_abi, signer=Signer.Keys(self.keypair), deploy_set=self.main_deploy_set,
                    call_set=call_set)
        encoded = self.client.abi.encode_message(params=encode_params)
        self.send_grams(address=encoded.address)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        return result, encoded.address

    def create_user(self,address,metadata):
        id_minted = self.get_total_minted(address)
        call_set = CallSet(
                function_name='mintNft', input={'metadata': metadata})
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)

        print(f"User address: {self.get_data(address,int(id_minted,16),metadata)}")
        return result

    def add_user_data(self,address,metadata):
        call_set = CallSet(
                function_name='addMessage', input=dict(amsg=metadata))
        encode_params = ParamsOfEncodeMessage(
            abi=self.data_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        return result

    def get_total_minted(self,address):
        call_set = CallSet(
            function_name='_totalMinted',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["_totalMinted"]

    def get_info(self,address):
        call_set = CallSet(
            function_name='getInfo',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.data_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.data_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["messages"]

    def get_data(self,address,total_minted,data):
        call_set = CallSet(
            function_name='resolveData',input=dict(addrRoot=address,id=total_minted,name=data)
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["addrData"]

    def get_open_key(self,address):
        call_set = CallSet(
            function_name='open',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        # run_params = ParamsOfRunExecutor(
        #     message=encoded_message.message, account=account_for_executor,
        #     abi=self.main_abi, return_updated_account=True)
        # result = self.client.tvm.run_executor(params=run_params)
        # run_params = ParamsOfRunExecutor(
        #     message=encoded_message.message, account=account_for_executor,
        #     abi=self.main_abi, return_updated_account=True)
        # result = self.client.tvm.run_executor(params=run_params)


        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return bytes.fromhex(result.decoded.output["open"])

    def get_proof_key(self,address):
        call_set = CallSet(
            function_name='m_pkey',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["m_pkey"]

    def get_answers(self,address):
        call_set = CallSet(
            function_name='available_choose',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["available_choose"]

    def get_private_key(self,address):
        call_set = CallSet(
            function_name='private_key',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return bytes.fromhex(result.decoded.output["private_key"])

    def get_ballot_num(self,address):
        call_set = CallSet(
            function_name='ballot_numbers_state',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["ballot_numbers_state"]

    def get_votes(self,address):
        call_set = CallSet(
            function_name='votes',
            )
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi,signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        encoded_message = self.client.abi.encode_message(
            params=encode_params)

        q_params = ParamsOfWaitForCollection(
            collection='accounts', result='id boc',
            filter={'id': {'eq': address}})
        account = self.client.net.wait_for_collection(params=q_params)

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["votes"]

    def finish_vote(self,address,private_key):
        call_set = CallSet(
                function_name='finish_vote', input={'_private': private_key.hex()})
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        return result

    def vote(self,address,proof,number,vote):
        # print(dict(proof=proof,ballot_number=number,vote=vote))
        call_set = CallSet(
                function_name='vote', input=dict(proof=proof,ballot_number=number,vote=vote.hex()))
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        #print(result.decoded.output)
        return result

        account_for_executor = AccountForExecutor.Account(
            boc=account.result['boc'], unlimited_balance=True)

        run_params = ParamsOfRunTvm(
            message=encoded_message.message, account=account.result["boc"], abi=self.main_abi)
        result = self.client.tvm.run_tvm(params=run_params)
        return result.decoded.output["votes"]

    def finish_vote(self, address, private_key):
        call_set = CallSet(
            function_name='finish_vote', input={'_private': private_key.hex()})
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        return result

    def vote(self, address, proof, number, vote):
        # print(dict(proof=proof,ballot_number=number,vote=vote))
        call_set = CallSet(
            function_name='vote', input=dict(proof=proof, ballot_number=number, vote=vote.hex()))
        encode_params = ParamsOfEncodeMessage(
            abi=self.main_abi, signer=Signer.NoSigner(), address=address,
            call_set=call_set)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = self.client.processing.process_message(
            params=process_params)
        # print(result.decoded.output)
        return result
