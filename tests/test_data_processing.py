import os
import unittest
import pandas as pd
from dotenv import load_dotenv
from moka_util.data_processing.data_cleaning import clean_moka_data

load_dotenv()


class Test(unittest.TestCase):

    def test_clean_moka_data(self):
        _path_data = os.path.join(
            os.environ["PATH_FOLDER_TEST_DATA"],
            os.environ["NAME_TEST_DATA_CLEANING_MOKA"],
        )
        _data_raw = pd.read_csv(_path_data, low_memory=False)
        df_cleaned = clean_moka_data(_data_raw)
        self.assertEqual(
            int(df_cleaned["Gross Sales"].sum()),
            int(os.environ["GROSS_SALES_AMOUNT_TEST"]),
            "Incorrect gross sales amount",
        )
        self.assertEqual(
            int(df_cleaned["Net Sales"].sum()),
            int(os.environ["NET_SALES_AMOUNT_TEST"], "Incorrect net sales amount"),
        )


if __name__ == "__main__":
    unittest.main()
