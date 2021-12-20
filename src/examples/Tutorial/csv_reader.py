import csv
import pandas as pd
import os


def tim_out_read(filename,rate):
    data = pd.read_csv(filename)
    print(data.time_out.values[-1])
    df = pd.DataFrame({'Uplink Rate': "{:.6f}".format(rate*(8 * 10 ** 3 )), 'Computation Completion Time': [data.time_out.values[-1]]})
    folder_name = os.path.splitext(filename)[0] + '_uplunk_rate_variation.csv'
    df.columns = ['Uplink Rate', 'Image Processing Time']
    df.to_csv(folder_name, mode='a', index=False, header=False)
    return str(folder_name)



