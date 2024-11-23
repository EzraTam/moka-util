import os
import json
import pandas as pd
path_jurnal_config = os.environ["JURNAL_CONFIG_PATH"]

# Load credentials.json
with open(path_jurnal_config, encoding="utf-8") as f:
    jurnal_config = json.load(f)


COLUMNS_JURNAL = jurnal_config["general"]["columns"]
jurnal_outlet_sales_config = jurnal_config["outlet"]

def transform_moka_to_jurnal(df: pd.DataFrame , outlet_name:str) -> pd.DataFrame:
    """ Function to transform moka data (cleaned by clean_moka_data)
    for upload to jurnal (https://my.jurnal.id)

    Args:
        df (pd.DataFrame): Cleaned MOKA Data
        outlet_name (str): Name of the outlet

    Raises:
        ValueError: _description_

    Returns:
        pd.DataFrame: Sales data in jurnal upload format
    """

    # Validations
    if outlet_name not in jurnal_outlet_sales_config.keys():
        raise ValueError("outlet_name is not contained in the jurnal_config! Check for possible misspelling or add the entry in jurnal_config.json")

    # Main functionality

    # Drop columns not used
    df = df.drop(columns=["Time","Net Sales","Refunds"])

    # Add customer columns
    df['*Customer']= jurnal_outlet_sales_config[outlet_name]["name"]

    list_col_nan = ['Email', 'BillingAddress', 'ShippingAddress', 'ShippingDate','ShipVia', 'TrackingNo','CustomerRefNo','Message', 'Memo', 'Description','Unit','InvoiceDiscount(value or %)', 'ShippingFee', 'WitholdingAccountCode', 'WitholdingAmount(value or %)', 'WarehouseName']

    for _col in list_col_nan:
        df[_col] = float('nan')

    df['*InvoiceDate'] = df["Date"].apply(lambda _date_str: _date_str.strftime('%d/%m/%Y'))
    df['*DueDate'] = df['*InvoiceDate']
    df = df.drop(columns=["Date"])

    df['*InvoiceNumber'] = df['Receipt Number'] 
    df = df.drop(columns=["Receipt Number"])

    df['*ProductName'] = [ f'{jurnal_outlet_sales_config[outlet_name]["product_name_prefix"]} | {_item_name} {"- "+_variant_name if isinstance(_variant_name,str) else ""}'for _name_outlet, _item_name, _variant_name in zip(df['*Customer'],df['Items'], df['Variant'])]
    df = df.drop(columns=['Items', 'Variant'])
    df = df.rename(columns={'Quantity': '*Quantity'})

    df['*UnitPrice'] = df['Gross Sales']/df['*Quantity']
    df['*UnitPrice'] = df['*UnitPrice'].apply(int)

    # Discounts still to check!
    df['ProductDiscountRate(%)'] = df['Discounts']/df['Gross Sales']
    df['ProductDiscountRate(%)'] = df['ProductDiscountRate(%)'].apply(lambda x: f'{round(float(x)*100,2)}%')

    df['TaxRate(%)'] = (df['Gratuity'] + df['Tax'])/(df['Gross Sales']-df['Discounts'])
    df['TaxRate(%)'] = df['TaxRate(%)'].apply(lambda x: f'{round(float(x)*100,2)}%')
    df['TaxName'] = float('nan') if jurnal_outlet_sales_config[outlet_name]['tax_name'] == '' else jurnal_outlet_sales_config[outlet_name]['tax_name']
    df = df.drop(columns = ['Gratuity', 'Tax', 'Gross Sales', 'Discounts'])

    df['#paid?(yes/no)'] = 'YES'

    df = df.rename(columns = {'Payment Method' : '#PaymentMethod'})

    df['#PaidToAccountCode'] = df['#PaymentMethod'].apply(lambda x: jurnal_outlet_sales_config[outlet_name]['payment_method_account'][x])
    df['Tags (use ; to separate tags)'] =  jurnal_outlet_sales_config[outlet_name]['tag']

    return df[COLUMNS_JURNAL].reset_index(drop = True)