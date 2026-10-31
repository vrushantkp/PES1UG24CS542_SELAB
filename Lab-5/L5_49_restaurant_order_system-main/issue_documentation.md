# Lab 5: Static Code Analysis --- Issue Documentation

**File analyzed:** `restaurant_order_system.py`\
**Tools used:** Pylint, Bandit, Flake8

## Issue documentation table

  ------------------------------------------------------------------------------------------------------------------
  Tool           Issue / Code        Severity or category  Description          Fix applied
  -------------- ------------------- --------------------- -------------------- ------------------------------------
  Pylint         `W0102` ---         Code quality          `placeTableOrder`    Changed the default to `None` and
                 dangerous default                         used a mutable list  initialized a new list inside the
                 value                                     (`[]`) as a default  function.
                                                           argument.            

  Pylint         `C0103` --- invalid Naming/style          Several function     Renamed them to snake_case and
                 function names                            names used camelCase updated their call sites.
                                                           rather than          
                                                           snake_case.          

  Pylint         `C0116` --- missing Documentation/style   Several functions    Added short docstrings describing
                 function docstrings                       did not have         each function.
                                                           docstrings.          

  Pylint         `C0301`, `C0209`    Style                 A line was too long  Split the long statement and changed
                 --- line length and                       and a regular string the message to an f-string.
                 string formatting                         used `%` formatting. 

  Pylint         `W0702` --- bare    Error handling        The exception        Changed it to catch `KeyError`.
                 exception                                 handler caught every 
                                                           exception type.      

  Pylint         `C0121`, `R1703`,   Style                 The code compared a  Used `is None` and simplified the
                 `R1705` ---                               value with `None`    return logic.
                 comparison and                            using `==` and had   
                 conditional style                         an unnecessary       
                                                           `else`.              

  Pylint         `W0611`, `W0612`    Code quality          `math`,              Removed the unused import and
                 --- unused                                `service_tax`, and   variable, and iterated over values
                 import/variables                          the loop variable    directly.
                                                           were unused.         

  Pylint         `W1514`, `R1732`    Code quality          The file was opened  Used a
                 --- file handling                         without an explicit  `with open(..., encoding="utf-8")`
                                                           encoding and was     context manager.
                                                           closed manually.     

  Pylint         `W0621` ---         Naming/style          A function parameter Renamed the parameter to
                 redefined outer                           reused the global    `order_data`.
                 name                                      name `orders`.       

  Bandit         `B307` --- use of   Medium                Evaluating an        Removed `eval()` and explicitly
                 `eval()`                                  arbitrary expression handled the program's existing
                                                           can execute unsafe   `base_bill * 0.90` discount
                                                           code.                expression. Other expressions now
                                                                                return the base bill, so this is a
                                                                                behavior change that should be
                                                                                noted.

  Bandit         `B324` --- weak MD5 High                  MD5 is not           Replaced MD5 with SHA-256. Generated
                 hash                                      appropriate when a   ticket hashes therefore change.
                                                           strong hash is       
                                                           required.            

  Bandit         `B311` ---          Low                   `random.randint()`   Replaced it with
                 non-cryptographic                         is not intended for  `secrets.randbelow()` while
                 random generator                          security-sensitive   retaining the four-digit range.
                                                           PIN generation.      

  Bandit         `B605` --- shell    High                  `os.system()` built  Removed the shell call and printed
                 command execution                         and executed a shell the same notification using Python.
                                                           command using a      This displays a message; it does not
                                                           filename.            print to a physical printer.

  Flake8         `E501` --- line too Formatting            A line exceeded the  Split the discounted-bill print
                 long                                      configured           statement across multiple lines.
                                                           79-character limit.  

  Flake8         `E122` ---          Formatting            The wrapped          Corrected the indentation of the
                 continuation                              statement's          wrapped statement.
                 indentation                               continuation line    
                                                           was incorrectly      
                                                           indented.            
  ------------------------------------------------------------------------------------------------------------------

## Verification results

  Tool     Original result                       Final result
  -------- ------------------------------------- ----------------------
  Pylint   4.81/10                               10.00/10
  Bandit   5 findings: 2 high, 1 medium, 2 low   No issues identified
  Flake8   Multiple formatting/style findings    No errors reported

## Notes

-   The required tool-fix commits were created separately for Pylint,
    Bandit, and Flake8.
-   The original and final reports are saved as `pylint_before.txt`,
    `pylint_after.txt`, `bandit_before.txt`, `bandit_after.txt`,
    `flake8_before.txt`, and `flake8_after.txt`.
-   The security changes intentionally alter some behavior: ticket
    hashes use SHA-256 instead of MD5