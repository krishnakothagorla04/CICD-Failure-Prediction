"""A tiny sample application used to demonstrate the CI/CD pipeline.
The point of this project is the pipeline + ML prediction gate, not the app.
"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    return a ** b
