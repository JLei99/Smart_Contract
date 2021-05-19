from pyteal import *


# In this smart contract, company pay staff1 salary1 and staff2 salary2 everymonth for one year

""" 
    defined default constant
"""

limit_fee = Int(10000)
period = Int(1)
dur = Int(1)
lease= Bytes("base64", "023sdDE2")
salary1 = Int(4000)
salary2 = Int(5000)
staff1 = Addr("6ZHGHH5Z5CTPCF5WCESXMGRSVK7QJETR63M3NY5FJCUYDHO57VTCMJOBGY")
staff2 = Addr("7Z5PWO2C6LFNQFGHWKSK5H47IQP5OJW2M3HA2QPXTY3WTNP5NU2MHBW27M")
company = Addr("ZZAF5ARA4MEC5PVDOP64JM5O5MQST63Q2KOY2FLYFLXXD3PFSNJJBYAFZM")
timeout = Int(12)


def salary_payment(limit_fee=limit_fee,
                     period=period,
                     dur=dur,
                     lease=lease,
                     salary1=salary1,
                     salary2=salary2,
                     staff1=staff1,
                     staff2=staff2,
                     company=company,
                     timeout=timeout):
    

    salary_pay_core = And(
        # make sure type of tranaction is payment
        Txn.type_enum() == TxnType.Payment,
        # make sure the transaction fee is a resonable amount(for protection)
        Txn.fee() < limit_fee,
        # make sure the relationships among period, durationa and timeout are valid
        Txn.first_valid() % period == Int(0),
        Txn.last_valid() == dur + Txn.first_valid(),
        # used for replay protection
        Txn.lease() == lease,
    )

    salary_pay_transfer = And(
        # the first transaction is company -> staff1
        # the second transaction is company -> staff2
        # make sure the first transaction and the second transaction have the same sender
        Gtxn[0].sender() == Gtxn[1].sender(),
        # Ensure that CloseRemainderTo is not set during a valid transaction.
        Txn.close_remainder_to() == Global.zero_address(),
        # make sure the reciever is correct for each transaction
        Gtxn[0].receiver() == staff1,
        Gtxn[1].receiver() == staff2,
        # make sure the amount of transaction is correct
        Gtxn[0].amount() == salary1 ,
        Gtxn[1].amount() == salary2
    )

    salary_pay_close = And(
        # when we close the contract, all the remaining money goes to company
        Txn.close_remainder_to() == company,
        Txn.rekey_to() == Global.zero_address(),
        Txn.receiver() == Global.zero_address(),
        Txn.first_valid() == timeout,
        Txn.amount() == Int(0)
    )
    
    salary_pay_escrow = salary_pay_core.And(salary_pay_transfer.Or(salary_pay_close))

    return salary_pay_escrow

""" 
    transfer Pyteal to TEAL
"""

if __name__ == "__main__":
    print(compileTeal(salary_payment(), mode=Mode.Signature, version=2
                     ))
