def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Cannot divide by zero"
    return a / b


print("1. Addition")
print("2. Subtraction")
print("3. Multiplication")
print("4. Division")

choice = input("Choose an operation: ")
if choice not in ["1", "2", "3", "4"]:
    print("Invalid choice. Please select a valid operation.")
    exit()

try:
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))

    if choice == "1":
        print("Result:", add(a, b))
    elif choice == "2":
        print("Result:", subtract(a, b))
    elif choice == "3":
        print("Result:", multiply(a, b))
    elif choice == "4":
        print("Result:", divide(a, b))
    else:
        print("Invalid choice")

except ValueError:
    print("Please enter valid numbers ")