import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from generate_customers import generate_customers
from generate_loans import generate_loans

SEED = 45


def monthly_payment(principal, annual_rate_pct, term_months):
    """Standard amortized loan payment (fixed amount each month)."""
    r = annual_rate_pct / 100 / 12
    return round(principal * r / (1 - (1 + r) ** -term_months), 2)


def generate_loan_payments(loans, customers):
    """Return a DataFrame of scheduled payments, linked to loans by loan_id."""
    random.seed(SEED)
    today = date.today()
    scores = customers.set_index("customer_id")["credit_score"]
    rows = []
    payment_number = 1

    for loan in loans.itertuples():
        start = date.fromisoformat(loan.start_date)
        amount = monthly_payment(loan.principal, loan.interest_rate, loan.term_months)

        # only payments already due as of today
        due_dates = [start + relativedelta(months=k) for k in range(1, loan.term_months + 1)]
        due_dates = [d for d in due_dates if d <= today]

        # bad loans miss their most recent payments
        if loan.status == "delinquent":
            missed = random.randint(1, 3)
        elif loan.status == "defaulted":
            missed = random.randint(4, 8)
        else:
            missed = 0
        first_missed = len(due_dates) - min(missed, len(due_dates))

        risk = float(np.clip((750 - scores[loan.customer_id]) / 450, 0, 1))
        p_late = 0.05 + 0.25 * risk

        for i, due in enumerate(due_dates):
            if i >= first_missed:
                paid_date, amount_paid = None, 0.0
            else:
                # late payers pay 5-25 days after due, others within a few days of it
                delay = random.randint(5, 25) if random.random() < p_late else random.randint(-2, 3)
                paid_date = min(due + timedelta(days=delay), today).isoformat()
                amount_paid = amount

            rows.append(
                {
                    "payment_id": f"P{payment_number:07d}",
                    "loan_id": loan.loan_id,
                    "due_date": due.isoformat(),
                    "paid_date": paid_date,
                    "amount_due": amount,
                    "amount_paid": amount_paid,
                }
            )
            payment_number += 1
    return pd.DataFrame(rows)


if __name__ == "__main__":
    customers = generate_customers(200)
    loans = generate_loans(customers)
    payments = generate_loan_payments(loans, customers)
    print(payments.head(10).to_string())
    print(len(payments), "payments for", len(loans), "loans")

    merged = payments.merge(loans[["loan_id", "status"]], on="loan_id")
    print("missed payments by loan status:")
    print(merged.groupby("status")["paid_date"].apply(lambda s: s.isna().sum()))