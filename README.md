Package containing helper-module for working with POS-Data hosted in Moka (https://www.mokapos.com/)

Implemented Functionalities:
✅ Query sales data from Moka (function: moka_util.query_web.query_sales_data)

Functionalities planned to be implemented:
👷 Cleaning sales data for data science/analytics purposes
👷 Query table management data
👷 Query loyalties data

Before Start:
- Add a json called 'credentials.json' containing credentials to the Moka-Account with entries of the form:
    - Key: Name of the outlet. You may specify this arbitrarily. Used only for reference.
    - Value: A dictionary with entries:
        - "email": Email for the login
        - "password": Password for the Moka
        - "outlet_id": Outlet ID specified in the Moka (Check in the developer window)

- Add environment variable containing the path to the credentials.json
