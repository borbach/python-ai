import matplotlib.pyplot as plt

def fibonacci(n):
    """Generates the Fibonacci sequence up to the nth term.

    Args:
        n: The number of terms in the sequence.

    Returns:
        A list containing the Fibonacci sequence.
    """

    fib_seq = [0, 1]
    for i in range(2, n):
        fib_seq.append(fib_seq[i-1] + fib_seq[i-2])
    return fib_seq

# Generate the Fibonacci sequence up to the 15th term
n = 15
fib_seq = fibonacci(n)

# Plot the Fibonacci sequence
plt.plot(range(1, n+1), fib_seq)
plt.xlabel('Term')
plt.ylabel('Value')
plt.title('Fibonacci Sequence')
plt.grid(True)
plt.show()

