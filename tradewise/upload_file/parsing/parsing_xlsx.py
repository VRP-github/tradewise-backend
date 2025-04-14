import pandas as pd
from datetime import datetime
import logging


def parsing_xlsx(xlsx_df):
    try:
        xlsx_df = xlsx_df.iloc[2:].reset_index(drop=True)

        valid_rows = []
        parsed_data = []

        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }

        for index, row in xlsx_df.iterrows():
            row = row.astype(str)

            if 'TOTAL' in row.iloc[4]:
                break
            if len(row) < 9 or row.iloc[2] == 'BAL':
                continue

            try:
                transaction_str = row.iloc[4]
                parts = transaction_str.split()

                action = parts[0]  # BOT or SOLD
                qty = int(parts[1])
                symbol = parts[2]
                size = int(parts[3])
                expiration = ' '.join(parts[5:8])  # E.g., '12 MAR 24'
                strike = int(parts[8])
                option_type = parts[9]  # CALL or PUT
                price = float(parts[10].replace('@', ''))

                # Construct transaction details similar to CSV logic
                exec_time_str = row.iloc[0]
                exec_time = pd.to_datetime(exec_time_str, format='%Y-%m-%d %H:%M:%S', errors='coerce')
                if pd.isna(exec_time):
                    continue

                side = 'BUY' if action == 'BOT' else 'SELL'
                pos_effect = 'TO OPEN' if action == 'BOT' else 'TO CLOSE'

                # Extract date components for identifier
                exp_parts = expiration.strip().split()
                if len(exp_parts) == 3:
                    day = exp_parts[0].zfill(2)
                    month = month_map.get(exp_parts[1].upper())
                    year = exp_parts[2]
                else:
                    continue

                identifier = f"{symbol}{year}{month}{day}{option_type[0]}{strike}"

                parsed_data.append({
                    'Exec Time': exec_time,
                    'Spread': 'SINGLE',
                    'Side': side,
                    'Qty': qty,
                    'Pos Effect': pos_effect,
                    'Symbol': symbol,
                    'Exp': expiration,
                    'Strike': strike,
                    'Type': option_type,
                    'Price': price,
                    'Net Price': price,
                    'Order Type': 'MKT',
                    'Transaction_Detail_ID': identifier
                })

            except Exception as e:
                logging.warning(f"Skipping row {index} due to error: {e}")
                continue

        if not parsed_data:
            return pd.DataFrame()

        df_result = pd.DataFrame(parsed_data)
        df_result = df_result.sort_values(by='Exec Time').reset_index(drop=True)

        return df_result

    except Exception as e:
        logging.error(f"Error parsing XLSX file: {e}")
        return pd.DataFrame()