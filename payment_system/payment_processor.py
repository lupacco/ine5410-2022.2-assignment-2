import time
from threading import Thread

from typing import Tuple
from globals import banks

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.currency import Currency
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

        while True:
            try:
                transaction = queue.pop(0)

                LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {queue}")
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
            time.sleep(3 * time_unit)  # Remova esse sleep após implementar sua solução!

        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self._bank_id} foi finalizado.")

    def new_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        #identificador de banco origem -> origin[0]
        origin_bank_id = origin[0]
        #identificador de banco destion -> destination[0]
        destination_bank_id = destination[0]
        # identificador da conta origem -> origin[1]
        origin_account = banks[origin_bank_id].accounts[origin[1]]
        #resgata conta destino
        destination_account = banks[destination_bank_id].accounts[destination[1]]

        #se for possível fazer a transferência/saque
        withdraw_requisition = origin_account.withdraw(amount)
        print(withdraw_requisition)

        if(withdraw_requisition[0]):
            #Em caso de ser uma transferência Nacional
            if(origin_bank_id == destination_bank_id):
                    #se for com cheque especial
                    if(withdraw_requisition[1] == "overdrafted"):
                        #taxa cobrada pelo banco
                        bank_tax = amount*0.05
                        #cobrança da taxa destino (retirado da conta origem)
                        origin_account.withdraw(bank_tax)
                        origin_bank = banks[origin_bank_id]
                        #incremento dos lucros acumulados do banco
                        origin_bank.total_profit += bank_tax
                        #deposito da taxa na conta do banco
                        origin_bank.reserves.currency.deposit(bank_tax)
                    #deposita quantia na conta destino
                    destination_account.deposit(amount)
            #Em caso de transferência Internacional
            else:
                bank_tax = amount*0.01
                if(withdraw_requisition[1] == "overdrafted"):
                    bank_tax = amount*0.06
                    origin_account.withdraw(bank_tax)
                #deposita na conta especial da currency origem
                origin_bank = banks[origin_bank_id]
                origin_bank.total_profit += bank_tax
                origin_bank.reserves.currency.deposit(amount + bank_tax)
                #converte quantia
                destination_currency = destination_account.currency
                converted_amount = currency.get_exchange_rate(currency, destination_currency)*amount
                #faz o saque na conta especial da currency destino
                origin_bank.reserves.destination_currency.withdraw(converted_amount)
                
                #depositando na conta destino
                destination_account.deposit(converted_amount)
            #incrementa operações realizadas pelo banco
            origin_bank.released_operations += 1


                
                
        

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

        self.new_transfer(transaction.origin, transaction.destination, transaction.currency)
        
        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        transaction.set_status(TransactionStatus.SUCCESSFUL)
        return transaction.status
