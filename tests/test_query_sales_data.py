import os
import unittest
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

os.environ["query_web_aether_credentials_path"] = os.environ[
    "TEST_QUERY_CREDENTIALS_PATH"
]

from moka_util.query_web.requests_util import query_sales_data


class Test(unittest.TestCase):

    def setUp(self):
        self.path_data = os.environ["PATH_FOLDER_TEST_DATA"]
        self.test_query_result_file_name = "test_result.csv"
        self.test_query_path_data_result = os.path.join(
            self.path_data, self.test_query_result_file_name
        )

    def test_query_sales(self):

        outlet_name = os.environ["TEST_QUERY_OUTLET_NAME"]
        start_date = os.environ["TEST_QUERY_START_DATE"]
        end_date = os.environ["TEST_QUERY_END_DATE"]

        query_sales_data(
            outlet_name,
            start_date,
            end_date,
            self.test_query_result_file_name,
            self.path_data,
        )
        path_data_validation = os.path.join(
            self.path_data, os.environ["TEST_QUERY_VALIDATION_DATA_NAME"]
        )

        self.assertTrue(
            pd.read_csv(self.test_query_path_data_result).equals(
                pd.read_csv(path_data_validation)
            ),
            "Queried data and the indeed data is not the same",
        )

    def tearDown(self):
        os.remove(self.test_query_path_data_result)


if __name__ == "__main__":
    unittest.main()
