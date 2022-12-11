import time
from threading import Thread, Condition, Lock

from typing import Tuple
from globals import banks

from globals import *
from payment_system.bank import Bank
from payment_system.account import Account
from utils.transaction import Transaction, TransactionStatus
from utils.currency import *
from utils.logger import LOGGER


class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank

    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las 
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!")
        queue = banks[self.bank._id].transaction_queue

        while self.bank.operating:
            try:
                with banks[self.bank._id].queue_lock:
                    while (len(queue) == 0 and self.bank.operating):
                        banks[self.bank._id].item_in_queue.wait()
                    if not self.bank.operating:
                        break
                    transaction = queue.pop(0)
                LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {queue}")
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")

    def transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int) -> bool:
        # Get banks id
        origin_bank_id = origin[0]
        destination_bank_id = destination[0]
        
        # Get accounts id
        origin_account_id = origin[1]
        destination_account_id = destination[1]
        
        # Get banks objects
        origin_bank = banks[origin_bank_id]
        destination_bank = banks[destination_bank_id]
        
        # Get account objects
        origin_account = origin_bank.accounts[origin_account_id]
        destination_account = destination_bank.accounts[destination_account_id]
        
        # Define as currencies
        origin_currency = origin_bank.currency
        destination_currency = destination_bank.currency
        
        #Em caso de ser uma transferência Nacional
        if(origin_bank_id == destination_bank_id):
            successful_transaction, special_check_transaction = origin_account.withdraw(amount)
            if successful_transaction:
                if special_check_transaction:
                    bank_tax = int(amount * 0.05)
                    origin_bank.total_profit += bank_tax
                    origin_bank.deposit_to_reserve(origin_currency, bank_tax)
                    
                # Deposita quantia na conta destino
                destination_account.deposit(amount)
                
                origin_bank.released_operations += 1
                return True
            else:
                return False
        
        #Em caso de transferência Internacional
        else:          
            # Withdraw da origem
            local_currency_amount = int(1.01 * amount * get_exchange_rate(destination_bank.currency, origin_bank.currency))
            successful_transaction, special_check_transaction = origin_account.withdraw(local_currency_amount)
            
            if successful_transaction:
                # Deposito na conta do banco da moeda origem
                if special_check_transaction:
                    bank_tax = int(local_currency_amount * 0.05)
                    origin_bank.total_profit += bank_tax
                    origin_bank.deposit_to_reserve(origin_currency, local_currency_amount + bank_tax)
                else:
                    origin_bank.deposit_to_reserve(origin_currency, local_currency_amount)

                # Saque na conta do banco da moeda destino
                origin_bank.withdraw_from_reserve(destination_currency, amount)
                
                # Depositando na conta destino
                destination_account.deposit(amount)
                
                origin_bank.released_operations += 1
                return True
            else:
                return False
            
    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a 
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!")
        
        successful_transfer = self.transfer(transaction.origin, transaction.destination, transaction.amount)
        
        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)
        
        if successful_transfer:
            transaction.set_status(TransactionStatus.SUCCESSFUL)
        else: 
            transaction.set_status(TransactionStatus.FAILED)
        return transaction.status
