# General Information
Package containing helper-module for working with POS-Data hosted in Moka (https://www.mokapos.com/)

Implemented Functionalities:
✅ Query sales data from Moka (function: moka_util.query_web.query_sales_data)

Functionalities planned to be implemented:
👷 Cleaning sales data for data science/analytics purposes
👷 Query table management data
👷 Query loyalties data

# Before Start

## If you use query_web

- Add a json called 'credentials.json' containing credentials to the Moka-Account with entries of the form:
    - Key: Name of the outlet. You may specify this arbitrarily. Used only for reference.
    - Value: A dictionary with entries:
        - "email": Email for the login
        - "password": Password for the Moka
        - "outlet_id": Outlet ID specified in the Moka (Check in the developer window)

- Add environment variable (MOKA_CREDENTIALS_PATH) containing the path to the credentials.json

## If you use transform_moka_to_jurnal
- add a json called 'jurnal_config.json' with entries:
    - "general": General configurations containing the entries:
        - "columns": Columns that should occur in the jurnal data
    - "outlet": Specific outlet configurations with entries of the form:
        - Key: Name of the outlet. You may specify this arbitrarily. Used only for reference.
        - Value: A dictionary with entries:
            - "name": Name used for customer name in the jurnal data
            - "tax_name": Name used for tax name in the jurnal data
            - "product_name_prefix": Prefix for the product name,
            - "payment_method_account": List of payment methods with account codes of form:
                - Key: Payment method
                - Value: Account code
            - "tag": Tag used for the outlet in jurnal
- add the environment variable JURNAL_CONFIG_PATH specifying path to the jurnal_config.json

# Using the Tests

## Before Start
- Add data to be cleaned and specify how much the following quantity should be:
    - Gross sales
    - Net sales
- Add .env in the tests_folder containing the variables:
    - envs for test_data_processing
        - PATH_FOLDER_TEST_DATA: Path to the folder containing test data (previously prepared)
        - NAME_TEST_DATA_CLEANING_MOKA: Name of the data to be cleaned as test
        - GROSS_SALES_AMOUNT_VALIDATION: Validation quantity. How much should the gross sales be? 
        - NET_SALES_AMOUNT_VALIDATION: Validation quantity. How much should the net sales be?

    - envs for test_query_sales_data:
        - TEST_QUERY_OUTLET_NAME: Outlet name of the data to query for test
        - TEST_QUERY_START_DATE: Start date of the sales data
        - TEST_QUERY_END_DATE: End date of the sales data
        - TEST_QUERY_VALIDATION_DATA_NAME: Data for validating the query
        - TEST_QUERY_CREDENTIALS_PATH: Path to the credentials (credentials.json)