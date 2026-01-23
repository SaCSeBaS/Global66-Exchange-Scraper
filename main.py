from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.id import ID
from datetime import datetime
import requests
import os

def main(context):

    APP_WRITE_URL = os.environ.get('APP_WRITE_URL')
    APP_WRITE_PROJECT_ID = os.environ.get('APP_WRITE_PROJECT_ID')
    APP_WRITE_KEY = os.environ.get('APP_WRITE_KEY')
    APP_WRITE_DB_ID = os.environ.get('APP_WRITE_DB_ID')
    APP_WRITE_DB_TABLE_ID = os.environ.get('APP_WRITE_DB_TABLE_ID')

    url = "https://api.global66.com/quote/public"
    now = datetime.now()
    in_currency = "PEN"
    out_currency = "EUR"
    source = "https://www.global66.com/"

    # headers = {
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    #     "accept-encoding": "gzip, deflate, br, zstd",
    #     "accept-language": "en-US,en;q=0.7",
    #     "cookie": "cf_clearance=VU89Fv0KV1vMdqcCw0kYGO3aTfdlZnAVuuNuyYANWsk-1768848950-1.2.1.1-pIUfGDFSLfWY_.5gmSAke_F_42wpSf80FoQsP_fiFl02cHsE2QodG9iSUYiRunl1Z6U72MWCZFmeZMHZuehu1VwBmxqlY4QddISjikKRxeSAGxsXJODV0QflfT.hwtcS8NSSFC.UQK3meswSXey4gczB8twloswnWuivbyBNp4Q59pSH.OoUIYpByvvwxuF._HiQVldzc_oJy4AZQCsm5wggSZ7AxBU3xfohkWKuLN8",
    #     "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-platform": '"Windows"',
    #     "sec-fetch-dest": "document",
    #     "sec-fetch-mode": "navigate",
    #     "sec-fetch-site": "none",
    #     "sec-fetch-user": "?1",
    #     "sec-gpc": "1",
    #     "upgrade-insecure-requests": "1",
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    # }

    params = {
        "originRoute": "227",
        "destinationRoute": "36",
        "amount": "100",
        "way": "origin",
        "paymentType": "WIRE_TRANSFER"
    }

    try:
        context.log("Function started")

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        quote_data = data.get("quoteData", {})
        rate = quote_data.get("originToDestinationRate")

        if rate:
            context.log(f"Extraction DateTime: {now.isoformat()}")
            context.log(f"Extracted Rate: {rate}")

            client = Client()
            client.set_endpoint(APP_WRITE_URL)
            client.set_project(APP_WRITE_PROJECT_ID)
            client.set_key(APP_WRITE_KEY)

            tables_db = TablesDB(client)

            result = tables_db.create_row(
                database_id=APP_WRITE_DB_ID,
                table_id=APP_WRITE_DB_TABLE_ID,
                row_id=ID.unique(),
                data={
                    "date": now.isoformat(),
                    "in_currency": in_currency,
                    "out_currency": out_currency,
                    "exchange_rate": float(rate),
                    "source": source
                },
            )

            context.log("Row inserted successfully")
            context.log(f"status: success | rate: {rate}")

            return context.res.json({
                "status": "success",
                "rate": rate,
                "timestamp": now.isoformat()
            })

        else:
            context.log(f"status: error | message: Rate not found in the response.")
            return context.res.json({
                "status": "error",
                "message": "Rate not found in the response."
            })

    except requests.exceptions.RequestException as e:
        context.log(f"status: error | message: Network error - {e}")
        return context.res.json({
            "status": "error",
            "message": f"Network error: {e}"
        })
    
    except Exception as e:
        context.log(f"status: error | message: An error occurred - {e}")
        return context.res.json({
            "status": "error",
            "message": f"An error occurred: {e}"
        })