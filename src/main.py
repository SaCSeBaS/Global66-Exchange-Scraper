from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.id import ID
from datetime import datetime
import cloudscraper
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

    params = {
        "originRoute": "227",
        "destinationRoute": "36",
        "amount": "100",
        "way": "origin",
        "paymentType": "WIRE_TRANSFER"
    }

    try:
        context.log("Function started")

        scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "desktop": True
            }
        )

        response = scraper.get(url, params=params, timeout=30)

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

            tables_db.create_row(
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

            return context.res.json({
                "status": "success",
                "rate": rate,
                "timestamp": now.isoformat()
            })

        else:
            context.log("status: error | message: Rate not found in response")
            return context.res.json({
                "status": "error",
                "message": "Rate not found in the response."
            })

    except Exception as e:
        context.log(f"status: error | message: {str(e)}")
        return context.res.json({
            "status": "error",
            "message": str(e)
        })