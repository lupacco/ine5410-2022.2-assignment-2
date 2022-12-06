from typing import Tuple

from globals import banks

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
        self.number_of_accounts = len(self.accounts) #contagem de contas registradas no banco
        self.transaction_queue  = []
        self.released_operations = 0 #contagem de operações realizadas pelo banco
        self.total_profit = 0 #lucro acumulado pelo banco


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
                

        

    def get_all_acounts_balance(self, accounts):
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

        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")
        LOGGER.info(f"Saldos:\n -> USD: {self.reserves.USD.balance},\n -> EUR: {self.reserves.EUR.balance},\n -> GBP: {self.reserves.GBP.balance},\n -> JPY: {self.reserves.JPY.balance},\n -> CHF: {self.reserves.CHF.balance},\n -> BRL: {self.reserves.BRL.balance}\n Transferências realizadas: {self.released_operations}\nContas registradas: {self.number_of_accounts}\n Saldo total dos clientes: {self.get_all_acounts_balance(self.accounts)}\n Lucro acumulado: {self.get_total_profit()}")
