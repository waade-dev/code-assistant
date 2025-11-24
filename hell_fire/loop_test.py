def calculator():
    print("Simple Calculator. Type 'exit' to quit.")
    while True:
        expression = input("Enter expression: ")
        if expression.lower() == 'exit':
            print("Exiting calculator.")
            break
        try:
            result = eval(expression)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    calculator()
