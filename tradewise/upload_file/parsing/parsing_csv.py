import pandas as pd
import logging


def parsing_csv_trade_history(df):
    trade_history_df = df.copy()

    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }

    try:
        trade_history_df = trade_history_df.dropna(how='all')

        try:
            trade_history_df['Exec Time'] = pd.to_datetime(trade_history_df['Exec Time'], errors='coerce')
            trade_history_df = trade_history_df.dropna(subset=['Exec Time'])
        except Exception as e:
            logging.error(f"Error parsing date column: {e}")
            return None

        def extract_date_components(exp):
            exp = str(exp)
            if len(exp) == 9:
                year = exp[-2:]
                month = exp[3:6].upper()
                day = exp[:2].zfill(2)
            elif len(exp) == 8:
                year = exp[-2:]
                month = exp[2:5].upper()
                day = exp[:1].zfill(2)
            else:
                return None, None, None
            return year, month_map.get(month, None), day

        date_components = trade_history_df['Exp'].apply(extract_date_components)
        trade_history_df[['Year', 'Month', 'Day']] = pd.DataFrame(date_components.tolist(), index=trade_history_df.index)
        trade_history_df
        trade_history_df['Transaction_Detail_ID'] = (
                trade_history_df['Symbol'].str.replace(r'\W+', '', regex=True) +
                trade_history_df['Year'] +
                trade_history_df['Month'] +
                trade_history_df['Day'] +
                trade_history_df['Type'].str[0] +
                trade_history_df['Strike'].astype(int).astype(str)
        )

        trade_history_df = trade_history_df.drop(columns=trade_history_df.columns[0], axis=1)

        trade_history_df = trade_history_df.sort_values(
            by=['Exec Time'],
            ascending=[True]
        ).reset_index(drop=True)

        trade_history_df
        return trade_history_df

    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        return None


def parsing_csv_cash_balance(df):
    df
    start_keyword = "Cash Balance"
    end_keyword = "Futures Statements"
    transaction_summary_df = []

    try:
        start_index = df[df.iloc[:, 0].str.contains(start_keyword, case=False, na=False)].index[0]
        end_index = df[df.iloc[:, 0].str.contains(end_keyword, case=False, na=False)].index[0]
    except IndexError as e:
        logging.error(f"Error finding start or end index: {e}")
        return None

    try:
        transaction_summary_df = df.iloc[start_index:end_index].reset_index(drop=True)
        transaction_summary_df = transaction_summary_df.iloc[2:].reset_index(drop=True)

        transaction_summary_df = transaction_summary_df[
            ~transaction_summary_df.apply(
                lambda row: row.astype(str).str.contains("Account Statement", case=False, na=False).any(),
                axis=1)]

        transaction_summary_df = transaction_summary_df[
            ~transaction_summary_df.apply(lambda row: row.astype(str).str.contains("BAL", case=False, na=False).any(),
                                          axis=1)]

        columns_to_drop = [f"Unnamed: {i}" for i in range(9, 15)]
        transaction_summary_df = transaction_summary_df.drop(columns=columns_to_drop, errors='ignore')

        transaction_summary_df = transaction_summary_df.dropna()

        transaction_summary_df = transaction_summary_df.rename(columns={
            'Account Statement for 98317365SCHW (Individual) since 3/6/24 through 3/11/24': 'DATE',
            'Unnamed: 1': 'TIME',
            'Unnamed: 2': 'TYPE',
            'Unnamed: 3': 'REF #',
            'Unnamed: 4': 'DESCRIPTION',
            'Unnamed: 5': 'Misc Fees',
            'Unnamed: 6': 'Commissions & Fees',
            'Unnamed: 7': 'AMOUNT',
            'Unnamed: 8': 'BALANCE',
        })

        def generate_identifier(row):
            description = row['DESCRIPTION']
            description_split = description.split()
            if "(Weeklys)" in description_split:
                description_split.remove("(Weeklys)")
            description_ticker_idx = description_split.index("100")
            description_ticker = description_split[description_ticker_idx - 1]
            description_year = description_split[description_ticker_idx + 3]
            description_month = description_split[description_ticker_idx + 2]
            month_map = {
                'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            description_month_final = month_map.get(description_month)
            description_day = description_split[description_ticker_idx + 1]
            if len(description_day) == 1:
                description_day = f"0{description_day}"
            description_type = description_split[description_ticker_idx + 5]
            description_type = description_type[0:1]
            description_strike_price = description_split[description_ticker_idx + 4]
            base_identifier = f"{description_ticker}{description_year}{description_month_final}{description_day}{description_type}{description_strike_price}"
            return base_identifier


        transaction_summary_df['IDENTIFIER'] = transaction_summary_df.apply(generate_identifier, axis=1)
        transaction_summary_df
    except Exception as e:
        logging.error(f"Error slicing the DataFrame: {e}")
        return None

    return transaction_summary_df


def transaction_summary(df):
    summary_df = df.copy()
    summary_df['Net Price'] = pd.to_numeric(summary_df['Net Price'], errors='coerce')
    summary_df['Qty'] = pd.to_numeric(summary_df['Qty'], errors='coerce')
    summary_df['Total P/L'] = (100 * summary_df['Net Price'] * summary_df['Qty']).astype(int)
    TS_DF = {'data':[]}
    for identifier in summary_df['Transaction_Detail_ID'].unique():
        temp_df = summary_df[summary_df['Transaction_Detail_ID'] == identifier].copy()
        first_to_open_buy_idx = temp_df[(temp_df['Pos Effect'] == 'TO OPEN') | (temp_df['Side'] == 'BUY')].index.min()

        if pd.notna(first_to_open_buy_idx):
            temp_df = temp_df.loc[first_to_open_buy_idx:].copy()
            temp_df['Tally Qty'] = temp_df['Qty'].cumsum()
            total_tally = temp_df['Qty'].sum()
            temp_df['Total Tally'] = total_tally

            avg_buy_price = temp_df[temp_df['Side'] == 'BUY']['Net Price'].mean() * 100
            avg_buy_price = round(avg_buy_price, 3)

            avg_sell_price = None
            if total_tally == 0:
                avg_sell_price = (temp_df[temp_df['Side'] == 'SELL']['Net Price'].mean() * 100)
                avg_sell_price = round(avg_sell_price, 3)

            avg_profit_loss = temp_df['Total P/L'].mean()
            avg_profit_loss = round(avg_profit_loss, 3)

            trade_start_time = temp_df.loc[temp_df.index[0], 'Exec Time']
            trade_end_time = temp_df.loc[temp_df.index[-1], 'Exec Time'] if total_tally == 0 else None
            trade_type = temp_df.loc[temp_df.index[0], 'Type']
            trade_identifier = identifier
            trade_quantity = temp_df.loc[temp_df.index[-1], 'Total Tally'].astype(int)

            avg_buy_price = avg_buy_price if pd.notna(avg_buy_price) else None
            avg_sell_price = avg_sell_price if pd.notna(avg_sell_price) else None
            avg_profit_loss = avg_profit_loss if pd.notna(avg_profit_loss) else None
            ticker = temp_df.loc[temp_df.index[0], 'Symbol']
            is_processed = 'y' if total_tally == 0 else 'n'

            trade_start_time = trade_start_time.date() if trade_start_time else None
            trade_end_time = trade_end_time.date() if trade_end_time else None

            new_data = {
                'Trade Start time': trade_start_time,
                'Trade End time': trade_end_time,
                'Type': trade_type,
                'TICKER': ticker,
                'IDENTIFIER': trade_identifier,
                'QUANTITY': trade_quantity,
                'Avg_Buy_Price': avg_buy_price,
                'Avg_Sell_Price': avg_sell_price,
                'Profit/Loss': avg_profit_loss,
                'Is Processed': is_processed,
            }

            TS_DF['data'].append(new_data)
            TS_DF
    return TS_DF


