from typing import Tuple

from globals import banks

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency, format_money
from utils.logger import LOGGER
from threading import Lock, Condition


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
        self.reserves           = CurrencyReserves(_id)
        self.operating          = False
        self.accounts           = []
        self.number_of_accounts = 0  #Contagem de contas registradas no banco
        
        self.transaction_queue  = []
        self.queue_lock = Lock()
        self.item_in_queue = Condition(self.queue_lock)
        
        self.national_operations_count = 0  # Contagem de operações nacionais realizadas pelo banco
        self.national_operations_count_lock = Lock()
        
        self.total_operation_time = 0
        self.total_operation_time_lock = Lock()
        
        self.international_operations_count = 0  # Contagem de operações internacionais realizadas pelo banco
        self.international_operations_count_lock = Lock()
        
        self.total_profit = 0  # Lucro acumulado pelo banco
        self.total_profit_lock = Lock()

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = self.number_of_accounts

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)
        self.number_of_accounts += 1
        
    def deposit_to_reserve(self, currency: Currency, amount: int) -> None:
        if currency == Currency.USD:
            self.reserves.USD.deposit(amount)
        elif currency == Currency.EUR:
            self.reserves.EUR.deposit(amount)
        elif currency == Currency.GBP:
            self.reserves.GBP.deposit(amount)
        elif currency == Currency.JPY:
            self.reserves.JPY.deposit(amount)
        elif currency == Currency.CHF:
            self.reserves.CHF.deposit(amount)
        else:
            self.reserves.BRL.deposit(amount)

    def withdraw_from_reserve(self, currency: Currency, amount: int) -> None:
        if currency == Currency.USD:
            self.reserves.USD.withdraw(amount)
        elif currency == Currency.EUR:
            self.reserves.EUR.withdraw(amount)
        elif currency == Currency.GBP:
            self.reserves.GBP.withdraw(amount)
        elif currency == Currency.JPY:
            self.reserves.JPY.withdraw(amount)
        elif currency == Currency.CHF:
            self.reserves.CHF.withdraw(amount)
        else:
            self.reserves.BRL.withdraw(amount)

    def get_all_acounts_balance(self):
        sum = 0
        for account in self.accounts:
            account_balance = account.balance
            sum += account_balance

        return sum

    def get_total_profit(self):
        return self.total_profit

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
        
        total_operations = self.national_operations_count + self.international_operations_count
        if total_operations != 0:
            tempo_medio = self.total_operation_time / total_operations
        else:
            tempo_medio = 0.0
            
        info_message = f"Estatísticas do Banco Nacional {self._id}:\n\n" \
                       f"Saldos das reservas:\n"  \
                       f"  -> Reserva de USD:                             {format_money(self.reserves.USD.balance, Currency.USD)}\n" \
                       f"  -> Reserva de EUR:                             {format_money(self.reserves.EUR.balance, Currency.EUR)}\n" \
                       f"  -> Reserva de GBP:                             {format_money(self.reserves.GBP.balance, Currency.GBP)}\n" \
                       f"  -> Reserva de JPY:                             {format_money(self.reserves.JPY.balance, Currency.JPY)}\n" \
                       f"  -> Reserva de CHF:                             {format_money(self.reserves.CHF.balance, Currency.CHF)}\n" \
                       f"  -> Reserva de BRL:                             {format_money(self.reserves.BRL.balance, Currency.BRL)}\n\n" \
                       f"Transferências:\n"  \
                       f"  -> Transferências nacionais processadas:       {self.national_operations_count}\n" \
                       f"  -> Transferências internacionais processadas:  {self.international_operations_count}\n" \
                       f"  -> Transferências não processadas:             {len(self.transaction_queue)}\n" \
                       f"  -> Tempo médio de espera das transferências:   {tempo_medio:.2f} s\n\n" \
                       f"Outras informações:\n"  \
                       f"  -> Contas registradas:                         {self.number_of_accounts}\n" \
                       f"  -> Saldo total dos clientes:                   {format_money(self.get_all_acounts_balance(), self.currency)}\n" \
                       f"  -> Lucro acumulado pelo banco:                 {format_money(self.get_total_profit(), self.currency)}\n\n\n"         
        LOGGER.info(info_message)

