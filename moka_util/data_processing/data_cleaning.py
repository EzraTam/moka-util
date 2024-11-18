import pandas as pd


def drop_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns which are not used in the analysis

    Args:
        df (pd.DataFrame): DF to be cleaned

    Returns:
        pd.DataFrame: Cleaned DF
    """
    df = df.drop(columns=["Outlet"])
    df = df.drop(columns=["SKU"])
    df = df.drop(columns=["Served By"])
    df = df.drop(columns=["Brand"])
    df = df.drop(columns=["Event Type"])
    df = df.drop(columns=["Reason of Refund"])
    df = df.drop(columns=["Modifier Applied"])
    df = df.drop(
        columns=[
            "Discount Applied",
            "Sales Type",
            "Collected By",
            "Customer",
            "Payment Method",
        ]
    )
    return df


def get_refunds(df: pd.DataFrame) -> pd.DataFrame:
    """Extract refunds from POS-Sales Data (MOKA)

    Args:
        df (pd.DataFrame): POS-Sales Data

    Returns:
        pd.DataFrame: DF with all refund transactions
    """
    _refund = df.query("Refunds > 0").reset_index(drop=True)
    _refund["Items"] = _refund["Items"].apply(lambda x: x.split(" - ")[-1])
    return _refund


def merge_duplicates_in_items(df: pd.DataFrame) -> pd.DataFrame:
    """In the POS-Sales data, there might be rows representing
    the same item and variant (within a transaction).
    This function is used to deduplicate such data

    Args:
        df (pd.DataFrame): POS-Sales data to be deduplicated

    Returns:
        pd.DataFrame: _description_
    """
    _col_order = df.columns
    _cols_group = ["Receipt Number", "Items", "Variant"]
    _cols_max = ["Date", "Time"]
    _cols_first = ["Category"]
    _cols_sum = [
        "Quantity",
        "Gross Sales",
        "Discounts",
        "Refunds",
        "Net Sales",
        "Gratuity",
        "Tax",
    ]
    df = df.groupby(_cols_group, as_index=False, dropna=False).agg(
        {
            **{_col: "max" for _col in _cols_max},
            **{_col: "first" for _col in _cols_first},
            **{_col: "sum" for _col in _cols_sum},
        }
    )
    return df[_col_order]


def clean_moka_data(df: pd.DataFrame) -> pd.DataFrame:
    """Function to clean the POS-sales data obtained from MOKA
    Functionalities:
        - Deduplicate data
        - Delete refunded transactions

    Args:
        df (pd.DataFrame): Data to be cleaned

    Returns:
        pd.DataFrame: Cleaned data
    """
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    df = drop_unnecessary_columns(df)

    _refund = get_refunds(df)

    df_not_refund = df.query("Refunds==0").reset_index(drop=True)
    li_refund = list(_refund["Receipt Number"].unique())
    _filter = df_not_refund["Receipt Number"].apply(lambda x: x in li_refund)
    receipt_refunded = df_not_refund[_filter].reset_index(drop=True)
    receipt_not_refunded = df_not_refund[~_filter].reset_index(drop=True)

    receipt_refunded = merge_duplicates_in_items(receipt_refunded)
    receipt_not_refunded = merge_duplicates_in_items(receipt_not_refunded)
    _refund = merge_duplicates_in_items(_refund)

    receipt_refunded["price"] = (
        receipt_refunded["Gross Sales"] / receipt_refunded["Quantity"]
    )
    receipt_refunded["discounts_perc"] = (
        receipt_refunded["Discounts"] / receipt_refunded["Gross Sales"]
    )
    # # Get the number of items refunded
    _refund_grouped = _refund.groupby(
        ["Receipt Number", "Items", "Variant"], as_index=False, dropna=False
    ).agg({"Quantity": "sum"})

    receipt_refunded_cleaned = receipt_refunded.merge(
        _refund_grouped.rename(columns={"Quantity": "Quantity_Refunded"}),
        on=["Receipt Number", "Items", "Variant"],
        how="left",
    )
    receipt_refunded_cleaned = receipt_refunded_cleaned.fillna({"Quantity_Refunded": 0})
    receipt_refunded_cleaned["Quantity"] = (
        receipt_refunded_cleaned["Quantity"]
        + receipt_refunded_cleaned["Quantity_Refunded"]
    )
    receipt_refunded_cleaned = receipt_refunded_cleaned.query("Quantity>0").reset_index(
        drop=True
    )
    receipt_refunded_cleaned["Gross Sales"] = (
        receipt_refunded_cleaned["Quantity"] * receipt_refunded_cleaned["price"]
    )
    receipt_refunded_cleaned["Discounts"] = (
        receipt_refunded_cleaned["Gross Sales"]
        * receipt_refunded_cleaned["discounts_perc"]
    )
    receipt_refunded_cleaned["Net Sales"] = (
        receipt_refunded_cleaned["Gross Sales"] - receipt_refunded_cleaned["Discounts"]
    )
    receipt_refunded_cleaned = receipt_refunded_cleaned.drop(
        columns=["price", "discounts_perc", "Quantity_Refunded"]
    )

    data_processed_refund_cleaned = pd.concat(
        [receipt_not_refunded, receipt_refunded_cleaned]
    )
    data_processed_refund_cleaned = data_processed_refund_cleaned.sort_values(
        ["Date", "Receipt Number", "Category", "Items", "Variant"]
    )

    return data_processed_refund_cleaned
