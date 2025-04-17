import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crypto.isis import ISISInstance, ISISOracle

# Test parameters
n = 5       # secret vector dimension
m = 8       # line number of A
q = 97      # modulus
k = 3       # request number

# Create the instance and the oracle
instance = ISISInstance(n=n, m=m, q=q)
oracle = ISISOracle(A=instance.A, q=instance.q, k=k)

print(f"Matrix A :\n{instance.A}")
print(f"Modulus q : {q}\n")

# Tests the requests and responses
for i in range(k):
    t = oracle.query()
    t_last, x_last = oracle.samples[-1]

    # Checks that A @ x = t mod q
    t_expected = (oracle.A @ x_last) % oracle.q

    assert np.array_equal(t, t_expected), f"Error : t != A·x mod q at request {i}"
    assert np.array_equal(t, t_last), f"Error : output values != t stores"
    assert np.max(np.abs(x_last)) <= 1, f"Error : x is not short (allowed values : {-1, 0, 1})"

    print(f"Request {i + 1} sucessful")

# Test if the oracle accepts too many requests (here we test the 4th request)
try:
    oracle.query()
    print("Error : Oracle accepted too many requests")
except Exception as e:
    print("Success : Oracle sucessfully rejected the query")
    print(f"Exception : {e}")
