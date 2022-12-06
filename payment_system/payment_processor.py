import time
from threading import Thread

from typing import Tuple

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
        # identificador da conta origem -> origin[1]
        origin_account = self.accounts[origin[1]]
        # identificador da conta destino -> destination[1]
        #identificador de banco origem -> origin[0]
        origin_bank_id = origin[0]
        #identificador de banco destion -> destination[0]
        destination_bank_id = destination[0]

        #Em caso de ser uma transferência nacional
        if(origin_bank_id == destination_bank_id):
            #se for possível fazer a transferência/saque
            if(origin_account.withdraw(amount)[0]):
                #resgata conta destino
                destination_account = self.accounts[destination[1]]
                destination_account.deposit(amount)             
        else:
            #se for possível fazer a transferência/saque
            results_of_withdraw = origin_account.withdraw(amount)[0]
            if(results_of_withdraw[0]):
                #definir uma taxa de transação
                if(results_of_withdraw[1] == "normal"):
                    transfer_tax = amount*0.01
                if(results_of_withdraw[1] == "overdrafted"):
                    transfer_tax = amount*0.06
                origin_account.balance -= (amount  + transfer_tax)
                #Incrementa lucro total do banco
                self.total_profit += transfer_tax
                #resgata conta especial interna do banco
                bank_account = self.reserves.currency
                #resgata conta especial do banco destino que receberá o dinheiro convertido

                #transfere para a conta do banco destino

                #converte o dinheiro na conta destino


                #transfere pra conta destino

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
