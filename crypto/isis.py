import numpy as np

class ISISInstance:
    def __init__(self, n, m, q):
        """Creates a new instance of ISIS problem
        n: dimension of the secret vector (number of columns of A)
        m: number of equations (number of rows of A)
        q: modulus (used in the equations A.x mod q = t)
        """
        self.n = n
        self.m = m
        self.q = q
        
        self.A = np.random.randint(-q//2, q//2, size=(m, n)) # A is a m x n matrix
        self.secret_x = np.random.randint(-1, 2, size=n)     # x is a n-dimensional vector
        self.t = (self.A @ self.secret_x) % q                # t is a m-dimensional vector

class ISISOracle:
    def __init__(self, A, q, k):
        """Initializes an ISIS oracle instance
        A: ISIS instance matrix
        q: modulus used in the ISIS instance
        k: maximum number of queries allowed
        """
        self.A = A
        self.q = q
        self.k = k
        
        self.count = 0     # counter of queries
        self.samples = []  # history of queries

    def query(self):
        """
        Requests a new equation to the ISIS oracle
        Returns:
            t: a new equation of the form A.x mod q = t
        Raises:
            Exception: if the maximum number of queries is reached
        """
        # Check if we have reached the maximum number of queries
        if self.count >= self.k:
            raise Exception("Maximum number of queries reached")
        
        # Generate a short vector x
        x = np.random.randint(-1, 2, size=self.A.shape[1])
        
        # Compute the corresponding image
        t = (self.A @ x) % self.q
        
        # Add the sample to the history and increase the counter
        self.samples.append((t, x))
        self.count += 1
        return t
    
    def verify(self, x: np.ndarray, t: np.ndarray) -> bool:
        """
        Check if (x,t) is a valid solution

        Conditions :
        1. A * x ≡ t (mod q)
        2. Vector x has at most k non-zero components
        """
        # A·x modulo q
        mod_product = (self.A @ x) % self.q
        t_mod = t % self.q

        # Condition one
        if not np.array_equal(mod_product, t_mod):
            return False

        # Condition 2
        nombre_non_nuls = np.count_nonzero(x)
        
        return nombre_non_nuls <= self.k


