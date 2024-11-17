from colorama import Fore, Style
from tabulate import tabulate
import pandas as pd


class tabulateTable:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.tabulateData = self.reformat_data(data)
        self.print_table()

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
        print(
            tabulate(
                self.tabulateData,
                headers=self.df.columns,
                tablefmt="fancy_grid",
                colalign=("left", "left", "right"),
            )
        )
