import matplotlib.pyplot as plt

# Function to generate Fibonacci sequence
def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence

# Number of terms to generate
n_terms = 1000

# Generate the Fibonacci sequence
fib_sequence = fibonacci(n_terms)

# Print the Fibonacci sequence
print("Fibonacci Sequence:")
# print(fib_sequence)

# Create an x-axis for the plot (indices of the sequence)
x = list(range(n_terms))

# Plotting the Fibonacci sequence
plt.plot(x, fib_sequence, marker='o', linestyle='-', color='b', label='Fibonacci Sequence')
plt.title('Fibonacci Sequence')
plt.xlabel('Index')
plt.ylabel('Fibonacci Number')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()


