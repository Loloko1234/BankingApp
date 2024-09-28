from decimal import Decimal

class Loan:
    def __init__(self, user_id, db_manager):
        self.user_id = user_id
        self.db_manager = db_manager

    def request_loan(self, amount, interest_rate):
        self.db_manager.execute_query(
            "INSERT INTO loans (user_id, amount, interest_rate, remaining_balance, status) VALUES (%s, %s, %s, %s, 'active');", 
            (self.user_id, amount, interest_rate, amount)
        )

    def pay_loan(self, loan_id, payment_amount):
        loan = self.db_manager.execute_query("SELECT remaining_balance FROM loans WHERE id = %s AND user_id = %s;", (loan_id, self.user_id))
        if not loan:
            return False, "Loan not found"
        
        remaining_balance = loan[0][0]
        if payment_amount > remaining_balance:
            return False, "Payment amount exceeds the remaining balance"
        
        new_remaining = remaining_balance - payment_amount
        self.db_manager.execute_query(
            "UPDATE loans SET remaining_balance = %s, status = %s WHERE id = %s;", 
            (new_remaining, 'paid' if new_remaining == 0 else 'active', loan_id)
        )
        return True, "Payment successful"

    def get_loan_history(self):
        return self.db_manager.execute_query(
            "SELECT id, amount, interest_rate, remaining_balance, status, created_at FROM loans WHERE user_id = %s ORDER BY created_at DESC;", 
            (self.user_id,)
        )