import pytest
from calculator import ValueError, add, divide, factorial, fibonacci, gcd, is_prime, lcm, multiply, power, subtract


# ========================================
# AUTO-GENERATED TESTS
# Generated: 2026-02-12 13:27:59
# ========================================

# Test for function: add
def test_add():
    assert add(0, 0) == 0
    assert add(1, 1) == 2
    assert add(-1, -1) == -2
    assert add(1, -1) == 0
    with pytest.raises(TypeError):
        add("a", 1)
    assert add(1.5, 2.7) == 4.2

# Test for function: subtract
def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 4) == -4
    assert subtract(-1, 2) == -3
    assert subtract(-1, -2) == 1
    with pytest.raises(TypeError):
        subtract("a", 3)
    with pytest.raises(TypeError):
        subtract(3, "b")

# Test for function: multiply
def test_multiply():
    assert multiply(0, 5) == 0
    assert multiply(-3, -4) == 12
    assert multiply(1, 2) == 2
    with pytest.raises(TypeError):
        multiply("a", 5)
    assert multiply(2.5, 3) == 7.5

# Test for function: divide
def test_divide():
    assert divide(4, 2) == 2
    assert divide(-1, -3) == 0.3333333333333333
    with pytest.raises(ValueError):
        divide(10, 0)
    assert divide(-5, 2) == -2.5

# Test for function: power
def test_power():
    assert power(2, 3) == 8
    assert power(-1, 2) == 1
    assert power(0, 5) == 0
    assert power(-1, -2) == 1
    with pytest.raises(TypeError):
        power(10, "text")
    assert power(2, 0) == 1

# Test for function: factorial
def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(-1) == ValueError("Negative numbers do not have factorials")
    assert factorial(5) == 120
    assert factorial(10) == 3628800

# Test for function: is_prime
def test_is_prime():
    assert is_prime(25) == False
    assert is_prime(23) == True
    assert is_prime(-1) == False
    assert is_prime(0) == False
    assert is_prime(2) == True
    with pytest.raises(TypeError):
        is_prime("text")

# Test for function: fibonacci
def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
    assert fibonacci(-1) == "ValueError: Index cannot be negative"
    with pytest.raises(ValueError):
        fibonacci(-5)
    assert fibonacci(10) == 55

# Test for function: gcd
def test_gcd():
    assert gcd(12, 15) == 3
    assert gcd(-12, 15) == 3
    assert gcd(0, 15) == 15
    assert gcd(0, -15) == 15
    with pytest.raises(TypeError):
        gcd("a", 15)
    assert gcd(12, 12) == 12

# Test for function: lcm
def test_lcm():
    assert lcm(6, 7) == 42
    assert lcm(-3, 4) == 12
    assert lcm(0, 5) == 0
    assert lcm(-1, -2) == 2
    with pytest.raises(ValueError):
        lcm(0, 0)
    with pytest.raises(ValueError):
        lcm(-1, -0)

