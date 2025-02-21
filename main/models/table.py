"""File that handles creating table for cli or email"""

from datetime import datetime
from colorama import Fore, Style
from tabulate import tabulate
import pandas as pd
from babel.numbers import get_currency_symbol
from models.cache_manager import cache_manager


class TabulateTable:
    """Class that prepares table whether thats for cli or email"""

    def __init__(self, data):
        self.data = data
        self.df = pd.DataFrame(data)

        if "Ext Hours" in self.df.columns:
            account_currency = cache_manager.get_account_currency()
            col_name_ccy = f"Ext Hours {get_currency_symbol(account_currency)}"
            self.df.rename(columns={"Ext Hours": col_name_ccy}, inplace=True)

    def reformat_data(self, data):
        """Apply colour formatting for the numerical columns"""
        return [
            [
                (
                    self.color_change(row[column])
                    if column in ["Ext Hours %", "Ext Hours"]
                    else row[column]
                )
                for column in row
            ]
            for row in data
        ]

    def color_change(self, value):
        """Method to change colour within the df itself based on numeric value"""
        value = str(value)
        try:
            num = float(value.rstrip("%"))
            if num > 0:
                return Fore.GREEN + value + Style.RESET_ALL
            elif num < 0:
                return Fore.RED + value + Style.RESET_ALL

        except ValueError:
            return Fore.RED + value + Style.RESET_ALL

    def print_table(self):
        """Prints out the table, used for cli"""
        tabulate_data = self.reformat_data(self.data)
        align = (
            ("left", "left", "right")
            if len(tabulate_data[0]) == 3
            else ("left", "left", "right", "right")
        )
        print(
            tabulate(
                tabulate_data,
                headers=self.df.columns,
                tablefmt="fancy_grid",
                colalign=align,
            )
        )

    def prepare_html_table(self):
        """Converts the table for html, used for email"""
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_table = self.df.to_html(
            index=False, border=0, escape=False, classes="email-table"
        )
        style = """
        <style>
            .email-table {
                border-collapse: collapse;
                width: 100%;
            }
            .email-table th, .email-table td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            .email-table th {
                background-color: #f2f2f2;
            }
        </style>
        """

        full_html = f"""
        <html>
        <head>{style}</head>
        <body>
            <p>Daily LETF performance data:</p>
            {html_table}
            <p>junjun @ {current_datetime}</p>
        </body>
        </html>
        """
        return full_html
