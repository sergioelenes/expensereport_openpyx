import openpyxl
import pandas as pd

from pathlib import Path
import os


courrent_dir = os.getcwd()
dabase = 'expensedb.xlsx'
print(os.path.exists(dabase))
df = pd.read_excel('expensedb.xlsx', sheet_name='detail')
#df.style.format({'Amount': '${0:,.0f}'})
#pivot = df.pivot_table(values='Amount', index='Concept', columns='Month', aggfunc='sum', fill_value="-", margins=True, margins_name='Total')


print(courrent_dir)