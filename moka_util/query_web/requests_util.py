# 28.07.2025: It seems that the server does not accept IPv6 connection.
# --> Add timeout to switch to IPV4: https://stackoverflow.com/questions/62599036/python-requests-is-slow-and-takes-very-long-to-complete-http-or-https-request
import json
import logging
import os
import shutil
import time
import urllib
import zipfile
from typing import Optional

import requests

from moka_util.query_web.errors import ResultError

log = logging.getLogger(__name__)

path_credentials = os.environ["MOKA_CREDENTIALS_PATH"]

# Load credentials.json
with open(path_credentials, encoding="utf-8") as f:
    credentials = json.load(f)


def query_sales_data(
    outlet_name: str,
    start_date: str,
    end_date: str,
    file_name: Optional[str] = None,
    folder_path_resulting_data: Optional[str] = None,
):
    """_summary_

    Args:
        outlet_name (str): Reference name for the outlet for which we extract the data
        start_date (str): Start date for the sales data to be extracted
        end_date (str): End date for the sales data to be extracted
        file_name (Optional[str], optional): Name of the sales data extracted.
            Defaults to None. If None, than filename will be in the form:
                <outlet_name>__<start_date>__<end_date>.csv
        folder_path_resulting_data (Optional[str], optional): 
            Folder path where the resulting file will be saved. 
            Defaults to None. If None:
                The current working directory will be raised

    Raises:
        ValueError: outlet_name has to be contained in the credentials.json
        ValueError: The desired filename has to have .csv-ending.
        ResultError: No files in the downloaded zip.
        ResultError: There are multiple files in the downloaded zip.
        ResultError: File obtained is not of type csv
    """    

    if outlet_name not in credentials.keys():
        raise ValueError(
            f"outlet_name has to be contained in the credentials.json! Available outlet_name: {list(credentials.keys())}"
        )

    if file_name is None:
        file_name = f"{outlet_name}__{start_date}__{end_date}.csv"
        log.warning(
            """file_name was not specified in the argument. """
            """Output file will be per default named as %s""",
            file_name,
        )

    if folder_path_resulting_data is None:
        folder_path_resulting_data = os.getcwd()
        log.warning(
            """folder_path_resulting_data. """
            """Output file will be saved per default in as %s""",
            folder_path_resulting_data,
        )

    # Input Validations
    if file_name.split(".")[-1] != "csv":
        raise ValueError(
            f"The desired filename has to have .csv-ending! Current name: {file_name}"
        )

    # URLs
    url_export = "https://service-goauth.mokapos.com/exporting/v1/exports"
    url_login = "https://service-goauth.mokapos.com/account/v2/login"

    credentials_for_login = {
        "email": credentials[outlet_name]["email"],
        "password": credentials[outlet_name]["password"],
    }

    data_login = {"session": credentials_for_login}

    data_export_request = {
        "feature_name": "order-export-item-detail",
        "additional": {
            "start_time": f"{start_date}T00:00:00",
            "end_time": f"{end_date}T23:59:59",
            "outlet_id": credentials[outlet_name]["outlet_id"],
        },
    }

    # Make the request nice looking to avoid blacklisted
    headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}

    # Login
    log.info("👮 Login to Moka with email: %s...", data_login["session"]["email"])
    with requests.Session() as x:
        _response = x.post(url_login,headers=headers, json=data_login, timeout=5)
        access_token = _response.json()["access_token"]
    log.info("✅ Login Successful. Access Token obtained\n")

    # Add access token to headers
    headers["Authorization"] = access_token

    # Get ID-File for identifying download
    log.info(f"🙇 Requesting POS Data from {start_date} to {end_date}...")
    with requests.Session() as x:
        _response = x.post(
            url_export,
            json=data_export_request,
            headers=headers,
            timeout=5,
        )
        id_file = _response.json()["id"]

    log.info("✅ Data ID obtained!\n")

    _status = ""

    while _status != "SUCCESS":
        log.info("--> Send request for download link ...")
        with requests.Session() as x:
            url_request_download = (
                f"{url_export}/{id_file}"
            )
            _response = x.get(
                url_request_download, headers=headers, timeout=5
            )
            _response_json = _response.json()
            _status = _response_json["status"]
            log.info(f"--> Current Status: {_status}")
            file_url = _response_json["file_url"]
        if _status != "SUCCESS":
            log.info(
                "--> Current Status is not equal SUCCESS. ⏰ Wait for 5 seconds to restart request...\n"
            )
            time.sleep(5)
        else:
            log.info("--> Download link obtained ✅\n")

    _zip_data_nm = "data_temp.zip"

    # Download the retrieved files
    log.info("👷 Downloading data obtained...")
    _data_zip_temp_path = os.path.join(folder_path_resulting_data, _zip_data_nm)
    urllib.request.urlretrieve(file_url, _data_zip_temp_path)
    log.info("✅ Data in Zip-Format obtained!\n")

    # Unzip the corresponding file
    _folder_path_resulting_data_temp = os.path.join(folder_path_resulting_data, "temp")
    log.info("👷 Unzip the File...")
    with zipfile.ZipFile(_data_zip_temp_path, "r") as zip_ref:
        zip_ref.extractall(_folder_path_resulting_data_temp)
    log.info("✅ File unzipped\n")

    log.info("👷 Remove the zip!")
    os.remove(_data_zip_temp_path)
    log.info("✅ Successful!")

    log.info("👷 Rename the obtained file...")
    file_obtained = os.listdir(_folder_path_resulting_data_temp)

    # Only one files!
    if len(file_obtained) == 0:
        raise ResultError("No files in the Zip!")
    if len(file_obtained) > 1:
        raise ResultError(
            f"There are multiple files in the Zip! Number of files: {len(file_obtained)}"
        )

    file_obtained = file_obtained[0]
    _file_ending = file_obtained.split(".")[-1]

    if _file_ending != "csv":
        raise ResultError(
            f"File obtained is not of type csv, but of type: {_file_ending}"
        )

    shutil.move(
        os.path.join(_folder_path_resulting_data_temp, file_obtained),
        os.path.join(folder_path_resulting_data, file_name),
    )
    shutil.rmtree(_folder_path_resulting_data_temp)
