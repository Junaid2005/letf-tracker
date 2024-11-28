from colorama import Fore, Style
from tabulate import tabulate
import pandas as pd
from datetime import datetime


class tabulateTable:
    def __init__(self, data):
        self.data = data
        self.df = pd.DataFrame(data)

    def reformat_data(self, data):
        return [
            [row["Underlying"], row["LETF"], self.color_change(row["Change"])]
            for row in data
        ]

    def color_change(self, value):
        if not "%" in value:
            return value
        num = float(value.replace("%", ""))
        if num > 0:
            return Fore.GREEN + value + Style.RESET_ALL
        elif num < 0:
            return Fore.RED + value + Style.RESET_ALL

    def print_table(self):
        tabulateData = self.reformat_data(self.data)
        print(
            tabulate(
                tabulateData,
                headers=self.df.columns,
                tablefmt="fancy_grid",
                colalign=("left", "left", "right"),
            )
        )

    def prepare_html_table(self):
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
