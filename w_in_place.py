import pandas as pd

from utils import get_data_file_path

filepath = get_data_file_path()

table = pd.read_csv(filepath)
table.to_csv(filepath, index=False)
