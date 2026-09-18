RATES = {"USD": 1, "EUR": 2, "ADAFD": None}

target = "USD"

for k, v in RATES.items():
    if k == target: print("ok")
    else: print("err")

