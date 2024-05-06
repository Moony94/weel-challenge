# Setting Up and Running Tests for Django Application

This document provides instructions on how to set up and run tests for the Django application.

## Prerequisites

Before running the tests, ensure you have the following prerequisites installed:

- Python (version 3.11 or higher)
- Django (version 5.0.4 or higher)

## Running Tests

1. Run the Django test management command to execute the test suite:

    ```bash
    python manage.py test
    ```

2. Wait for the tests to complete. Django will output the test results to the console, indicating whether each test passed or failed.

3. Review the test results to identify any failing tests and take necessary actions to fix them.

## Additional Notes

- So many things that could be better for a production environment.

Improvements
1. !Background task queue
2. Flesh out admin for ops/cc tasks
3. Auth
4. Observability/Monitoring
5. DB encryption
# Tests
6. Need way more tests 
    - Full card balance suite
    - Auth suite
# Org
7. Add Organisation entity for Card - GET should be org specific
# Card
8. Create seperate control entities - Read speed, no need for a massive if/switch statement
9. Create seperate card number generator with check for if the cards been made
10. Card expiration date should be generated?
11. Card entity should define a method for dealing with the balance
# Transaction
12. reason_declined shouldn't be a CHAR field - Error entity?