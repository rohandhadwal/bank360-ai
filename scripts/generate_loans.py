import random
from datetime import date

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from faker import Faker

from generate_customers import generate_customers

SEED = 44

fake = Faker("en_US")
Faker.seed(SEED)
random.seed(SEED)
rng = np.random.default_rng(SEED)

LOAN_TYPES = {
    "personal": {"median": 8000, "sigma": 0.6, "terms": [12, 24, 36, 48, 60], "base_rate": 11.0},
    "auto": {"median": 22000, "sigma": 0.4, "terms": [36, 48, 60, 72], "base_rate": 6.5},
    "mortgage": {"median": 250000, "sigma": 0.4, "terms": [180, 360], "base_rate": 5.5},
}
TYPE_WEIGHTS = [0.50, 0.30, 0.20]


def generate_loans(customers):
    """Return a DataFrame of loans, linked to customers by customer_id."""
    today = date.today()
    rows = []
    loan_number = 1
    for c in customers.itertuples():
        for _ in range(random.choices([0, 1, 2], [0.65, 0.30, 0.05])[0]):
            loan_type = random.choices(list(LOAN_TYPES), TYPE_WEIGHTS)[0]
            profile = LOAN_TYPES[loan_type]

            # affordability rule: loan capped at 4x income, rounded to nearest 100
            principal = rng.lognormal(np.log(profile["median"]), profile["sigma"])
            principal = int(round(min(principal, 4 * c.annual_income), -2))

            # risk: 0 for a score of 750+, rising to 1 at a score of 300
            risk = float(np.clip((750 - c.credit_score) / 450, 0, 1))
            rate = round(profile["base_rate"] + 8 * risk + float(rng.normal(0, 0.5)), 2)

            term = random.choice(profile["terms"])
            earliest = max(date.fromisoformat(c.signup_date), today - relativedelta(years=6))
            start = fake.date_between(start_date=earliest, end_date="today")
            end = start + relativedelta(months=term)

            # lower scores are more likely to become delinquent or default
            p_delinquent = 0.03 + 0.15 * risk
            p_default = 0.02 + 0.15 * risk
            outcome = random.choices(
                ["good", "delinquent", "defaulted"],
                [1 - p_delinquent - p_default, p_delinquent, p_default],
            )[0]
            if start > today - relativedelta(months=3):
                outcome = "good"  # too new to have gone bad

            if outcome == "good":
                status = "paid_off" if end < today else "current"
            else:
                status = outcome

            rows.append(
                {
                    "loan_id": f"L{loan_number:06d}",
                    "customer_id": c.customer_id,
                    "loan_type": loan_type,
                    "principal": principal,
                    "interest_rate": rate,
                    "start_date": start.isoformat(),
                    "term_months": term,
                    "status": status,
                }
            )
            loan_number += 1
    return pd.DataFrame(rows)


if __name__ == "__main__":
    customers = generate_customers(200)
    loans = generate_loans(customers)
    print(loans.head(10).to_string())
    print(loans["status"].value_counts())
    print(loans["loan_type"].value_counts())