class BankAccount:
    bank_name = "Python National Bank"
    interest_rate = 0.03

    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self.balance = initial_balance
        self.transactions = []

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"+{amount:.2f}")
            return f"Deposited {amount:.2f}. New balance: {self.balance:.2f}"
        return "Deposit amount must be positive."

    def withdraw(self, amount):
        if amount > self.balance:
            return "Insufficient funds."
        self.balance -= amount
        self.transactions.append(f"-{amount:.2f}")
        return f"Withdrew {amount:.2f}. New balance: {self.balance:.2f}"

    def get_summary(self):
        return (
            f"Account Owner : {self.owner}\n"
            f"Bank          : {BankAccount.bank_name}\n"
            f"Balance       : {self.balance:.2f}\n"
            f"Transactions  : {', '.join(self.transactions) or 'None'}"
        )

account1 = BankAccount("Alice", 1000)
account2 = BankAccount("Bob")

print("\n--- BankAccount Class ---")
print(account1.deposit(500))
print(account1.withdraw(200))
print(account1.get_summary())

print(f"\nBoth accounts use: {BankAccount.bank_name}")
print(f"Account1 bank: {account1.bank_name}")
print(f"Account2 bank: {account2.bank_name}")