from decimal import Decimal

class Account:
    def __init__(self, user_id, db_manager):
        self.user_id = user_id
        self.db_manager = db_manager

    def check_balance(self):
        result = self.db_manager.execute_query("SELECT balance FROM accounts WHERE user_id = %s;", (self.user_id,))
        return result[0][0] if result else Decimal('0')

    def update_balance(self, amount, operation):
        current_balance = self.check_balance()
        new_balance = current_balance + amount if operation == 'deposit' else current_balance - amount
        self.db_manager.execute_query("UPDATE accounts SET balance = %s WHERE user_id = %s;", (new_balance, self.user_id))
        return new_balance