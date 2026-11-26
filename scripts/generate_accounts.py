import random  # built-in: random choices
from datetime import date

import numpy as np
import pandas as pd 
from faker import Faker

from generate_customers import generate_customers  # our customer generator

SEED = 43

fake = Faker("en_US")
Faker.seed(SEED)
random.seed(SEED)
rng = np.random.default_rng(SEED)

# typical balance (median) and spread for each account type
BALANCE_PROFILE = {
    "checking": (3000, 1.0),
    "savings": (8000, 1.1),
    "credit_card": (1500, 0.9),  # for credit cards, balance = amount owed
}


def generate_accounts(customers):
    """Return a DataFrame of accounts, linked to customers by customer_id."""
    rows = []
    account_number = 1
    for c in customers.itertuples():
        types = ["checking"]  # every customer has checking
        if random.random() < 0.60:
            types.append("savings")
        if random.random() < 0.40:
            types.append("credit_card")

        signup = date.fromisoformat(c.signup_date)
        for account_type in types:
            open_date = fake.date_between(start_date=signup, end_date="today")
            status = random.choices(["active", "dormant", "closed"], [0.90, 0.07, 0.03])[0]
            close_date = None
            if status == "closed":
                close_date = fake.date_between(start_date=open_date, end_date="today").isoformat()

            median, spread = BALANCE_PROFILE[account_type]
            balance = 0.0 if status == "closed" else round(float(rng.lognormal(np.log(median), spread)), 2)

            rows.append(
                {
                    "account_id": f"A{account_number:07d}",
                    "customer_id": c.customer_id,
                    "account_type": account_type,
                    "open_date": open_date.isoformat(),
                    "close_date": close_date,
                    "status": status,
                    "balance": balance,
                    "currency": "USD",
                }
            )
            account_number += 1
    return pd.DataFrame(rows)


if __name__ == "__main__":
    customers = generate_customers(10)
    accounts = generate_accounts(customers)
    print(accounts.to_string())