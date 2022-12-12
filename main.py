import argparse, time, sys
from logging import INFO, DEBUG
from random import randint

from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER
from datetime import datetime, timedelta


if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write('Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u", help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(INFO)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0
    
    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):
        
        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency)
        
        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))
        
        # Adiciona banco na lista global de bancos
        banks.append(bank)

    # Inicializa contas dos bancos
    for bank in banks:
        for i in range(100):
            bank.new_account(randint(100_00, 100_000_00), randint(0, 50_000_00))
                     
    # Armazena as threads
    threads_transaction_generator = []
    threads_payment_processor = []

    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    for i, bank in enumerate(banks):
        # Inicializa um TransactionGenerator thread por banco:
        thread = TransactionGenerator(_id=i, bank=bank)
        thread.start()
        threads_transaction_generator.append(thread)
        # Inicializa um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.
        for j in range(num_payment_processors): 
            thread = PaymentProcessor(_id=j, bank=bank)
            thread.start()
            threads_payment_processor.append(thread)
        
    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        time.sleep(time_unit)
        # Atualiza a variável tempo:
        t += 1
    
    # Fecha os bancos
    for bank in banks:
        bank.operating = False

    # Finaliza todas as threads
    for thread in threads_transaction_generator:
        thread.join()
    for thread in threads_payment_processor:
        thread.join()
        
    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")
    
    # Informações sobre a simulação
    for bank in banks:
        bank.info()
        
    # Informações gerais da simulação
    processed_operations = 0
    unprocessed_operations = 0
    total_time = 0
    for bank in banks:
        processed_operations += bank.national_operations_count + bank.international_operations_count
        unprocessed_operations += len(bank.transaction_queue)
        total_time += bank.total_operation_time
    tempo_medio = total_time / processed_operations
    info_message = f"Estatísticas gerais da simulação (todos os bancos):\n" \
                   f"Transferências processadas:               {processed_operations}\n" \
                   f"Transferências não processadas:           {unprocessed_operations}\n" \
                   f"Tempo médio de espera das transferências: {tempo_medio:.2f} s\n"    
    LOGGER.info(info_message)
