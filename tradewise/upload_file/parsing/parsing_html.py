import pandas as pd
from datetime import datetime
import logging


def parsing_html(html_file):
    try:
        html_file.seek(0)
        tables = pd.read_html(html_file, flavor='lxml', header=None)

        raw_data = []
        for table in tables:
            for row in table.values:
                row_str = " ".join([str(x) for x in row])
                if "TRD" in row_str and ("BOT" in row_str or "SOLD" in row_str):
                    raw_data.append(row)

        if not raw_data:
            logging.error("No valid trade rows found.")
            return pd.DataFrame()

        columns = [
            "Exec Time", "Action", "Quantity", "Symbol", "Size", "Weekly", "Day", "Month", "Year", "Strike", "Type", "Price", "Rest"
        ]
        df = pd.DataFrame(raw_data, columns=columns[:len(raw_data[0])])
        df = df.dropna(how='all')
        df['Exec Time'] = pd.to_datetime(df['Exec Time'], format='%m/%d/%y, %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['Exec Time'])

        df['Exp'] = df['Day'].astype(str).str.zfill(2) + ' ' + df['Month'].str.upper() + ' ' + df['Year'].astype(str)
        df['Qty'] = df['Quantity']
        df['Side'] = df['Action'].apply(lambda x: 'BUY' if 'BOT' in x else 'SELL')
        df['Pos Effect'] = df['Side'].apply(lambda x: 'TO OPEN' if x == 'BUY' else 'TO CLOSE')
        df['Order Type'] = 'MKT'
        df['Net Price'] = df['Price'].astype(str).str.replace('@', '', regex=False).astype(float)
        df['Price'] = df['Net Price']
        df['Spread'] = 'SINGLE'

        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
            'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }

        def generate_id(row):
            try:
                month = month_map.get(row['Month'].upper(), '00')
                day = str(row['Day']).zfill(2)
                strike = str(int(row['Strike']))
                return f"{row['Symbol']}{row['Year']}{month}{day}{row['Type'][0]}{strike}"
            except Exception as e:
                logging.warning(f"Failed to generate ID for row: {e}")
                return "INVALID_ID"

        df['Transaction_Detail_ID'] = df.apply(generate_id, axis=1)

        final_columns = [
            "Exec Time", "Spread", "Side", "Qty", "Pos Effect", "Symbol", "Exp", "Strike", "Type",
            "Price", "Net Price", "Order Type", "Transaction_Detail_ID"
        ]
        return df[final_columns].sort_values(by="Exec Time").reset_index(drop=True)

    except Exception as e:
        logging.error(f"Error parsing HTML file: {e}")
        return pd.DataFrame()