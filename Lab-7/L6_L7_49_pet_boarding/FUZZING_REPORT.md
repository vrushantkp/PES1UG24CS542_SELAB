# Lab 7: Fuzzing for Input Validation Bugs

**Student Name:** VRUSHANT K P  
**SRN:** PES1UG24CS542  
**Sl. No.:** 49  
**Assigned Module:** `pet_boarding.py`  
**Repository:** `L6_L7_49_pet_boarding`  
**Testing Frameworks:** `Hypothesis` + `pytest`  

---

## 1. Objective & Learning Outcomes
* Understand fuzz testing as a dynamic security and quality assurance technique.
* Apply property-based fuzzing using Python's **Hypothesis** library.
* Uncover hidden bugs, unhandled exceptions, and edge-case vulnerabilities caused by unexpected and malformed inputs.
* Improve code robustness and resilience using defensive programming practices.

---

## 2. Step 1: Initial Application Execution
The baseline script was executed using standard sample inputs:
* `Enter pet:days (e.g. dog:5):` `dog:5` -> Output: `('Dog', 5.0)`
* `Enter stay lengths in days as CSV (e.g. 2,5,7):` `2,5,7` -> Output: `4`
* `Enter fee|discount (e.g. 1500|100):` `1500|100` -> Output: `1670.0`

While working under standard happy-path inputs, the program completely lacked validation for missing delimiters, non-numeric values, negative numbers, empty strings, and `None` inputs.

### Terminal Output:
![Step 1: Initial Run](screenshot1_initial_run.png)

---

## 3. Step 2: Fuzz Testing with Hypothesis (Bug Detection)
A property-based test suite was written in `test_pet_boarding.py` specifying that functions must never crash on any arbitrary string or `None`:

```python
from hypothesis import given, strategies as st
from pet_boarding import parse_booking, stay_average, payable_fee

@given(st.text() | st.none())
def test_parse_booking_no_crash(s):
    try:
        parse_booking(s)
    except Exception as e:
        assert False, f"parse_booking crashed with: {e}"

@given(st.text() | st.none())
def test_stay_average_no_crash(s):
    try:
        stay_average(s)
    except Exception as e:
        assert False, f"stay_average crashed with: {e}"

@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {e}"
```

### Fuzzing Failures Discovered:
Running `pytest test_pet_boarding.py` caused all 3 functions to fail immediately:

| Function | Failing Inputs Uncovered | Unhandled Exception Raised |
| :--- | :--- | :--- |
| `parse_booking` | `None`, `""`, `"5"`, `"cat:abc"`, `"dog:cat:5"` | `AttributeError: 'NoneType' object has no attribute 'split'`, `ValueError: not enough values to unpack`, `ValueError: could not convert string to float` |
| `stay_average` | `None`, `""`, `"   "`, `"1,,3"`, `"foo,bar"` | `AttributeError: 'NoneType' object has no attribute 'split'`, `ZeroDivisionError: integer division or modulo by zero`, `ValueError: invalid literal for int()` |
| `payable_fee` | `None`, `""`, `"|"`, `"1500"`, `"abc|100"` | `AttributeError: 'NoneType' object has no attribute 'split'`, `ValueError: not enough values to unpack`, `ValueError: could not convert string to float` |

### Terminal Output (Test Failures):
![Step 2: Fuzz Tests Failing](screenshot2_fuzz_tests_failing.png)

---

## 4. Step 3: Defensive Code Hardening & Execution
To resolve every failure exposed by fuzz testing, `pet_boarding.py` was refactored with comprehensive defensive programming techniques:
1. **Type Checking:** Strictly ensured inputs are strings (`isinstance(text, str)`), returning safe defaults (`None`, `0`, `0.0`) on `None` or non-string types.
2. **Structural Validation:** Verified exact delimiter count (`':'` or `'|'`) before attempting to unpack.
3. **Safe Conversions:** Wrapped all `int()` and `float()` conversions in `try...except (ValueError, TypeError)` blocks.
4. **Division-by-Zero Guard:** Verified that the list of parsed integers is non-empty before performing integer division `//`.
5. **Boundary & Sanitization:** Stripped leading/trailing whitespace and validated against negative numbers and `NaN`.

### Terminal Output (Fixed Application Run):
![Step 3: Fixed Application Run](screenshot3_fixed_run.png)

---

## 5. Step 4: Verification with Hypothesis (All Passing)
Re-running the Hypothesis fuzz tests against the hardened module executed hundreds of dynamically generated inputs (special characters, emojis, null bytes, long strings, boundary floats).

All tests passed with **0 unhandled exceptions**:
```text
============================== 3 passed in 0.81s ==============================
```

### Terminal Output (Tests Passing):
![Step 4: Fuzz Tests Passing](screenshot4_fuzz_tests_passing.png)

---

## 6. Deliverables Summary

| Deliverable | File Name | Status |
| :--- | :--- | :---: |
| 1. Screenshot PDF Report | `PES1UG24CS542_Lab7_Report.pdf` | Generated with all 4 screenshots |
| 2. Fixed Application Script | `pet_boarding.py` | Hardened against all edge cases |
| 3. Updated Test Suite | `test_pet_boarding.py` | Complete Hypothesis Fuzz Suite |
| 4. Online Report Document | `FUZZING_REPORT.md` | Complete with tables & analysis |
