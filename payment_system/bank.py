from typing import Tuple

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER


class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
    
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves()
        self.operating          = False
        self.accounts           = []
        self.number_of_accounts = len(self.accounts)
        self.transaction_queue  = []
        self.released_operations = 0


    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)
        self.number_of_accounts += 1 #incrementa contador de contas no banco

    def new_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        #cria nova transação -> _ids correspondentes às posições da transação no array
        new_transaction = Transaction(len(self.transaction_queue), origin, destination, amount, currency)
        #insere transação na fila de transções -> não é necessário utilizar uma classe Queue, uma vez que o comportamento de uma fila pode ser reproduzido com append() e pop(0)
        self.transaction_queue.append(new_transaction)

    def get_all_acounts_balance(self, accounts):
        sum = 0
        for account in self.accounts:
            account_balance = account.balance
            sum += account_balance

        return sum

    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")
        LOGGER.info(f"Saldos:\n -> USD: {self.currency.USD},\n -> EUR: {self.currency.EUR},\n -> GBP: {self.currency.GBP},\n -> JPY: {self.currency.JPY},\n -> CHF: {self.currency.CHF},\n -> BRL: {self.currency.BRL}\n Transferências realizadas: {self.released_operations}\nContas registradas: {self.number_of_accounts}\n Saldo total dos clientes: {self.get_all_acounts_balance(self.accounts)}\n Lucro acumulado: IMPLEMENTAR!!!")
