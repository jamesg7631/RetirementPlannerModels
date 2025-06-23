

with open("Moneymarket_returns.csv") as new_file:
    stack = []
    for line in new_file:
        stack.append(line)
    
with open("Moneymarket_monthly_returns_GBP.csv", 'w') as my_file:
    while len(stack) > 0:
        line = stack.pop()
        my_file.write(line)