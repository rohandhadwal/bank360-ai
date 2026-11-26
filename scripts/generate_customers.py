import random  # built-in: random choices

import numpy as np 
import pandas as pd 
from faker import Faker  # realistic fake names, emails, phones

SEED = 42

fake = Faker("en_US")
Faker.seed(SEED)
random.seed(SEED)
rng = np.random.default_rng(SEED)

SEGMENTS = ["retail", "premium", "small_business"]
SEGMENT_WEIGHTS = [0.75, 0.15, 0.10]
BASE_INCOME = {"retail": 55000, "premium": 140000, "small_business": 90000}


def generate_customers(n=5000):
    """Return a DataFrame of n clean synthetic customers."""
    rows = []
    for i in range(1, n + 1):
        segment = random.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
        income = int(rng.lognormal(mean=np.log(BASE_INCOME[segment]), sigma=0.35))
        score = int(np.clip(rng.normal(690, 70), 300, 850))
        rows.append(
            {
                "customer_id": f"C{i:06d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85).isoformat(),
                "segment": segment,
                "country": "US",
                "signup_date": fake.date_between(start_date="-10y", end_date="today").isoformat(),
                "annual_income": income,
                "credit_score": score,
                "is_test": "N",
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_customers(10)
    print(df.to_string())