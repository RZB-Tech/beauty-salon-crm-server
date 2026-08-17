def foo(*args, **kwargs):
    print(f"{args}\n{kwargs}")

foo(4, status = "CANCELLED")