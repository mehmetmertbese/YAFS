import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
filename = folder_results + "sim_trace_full_r4_n20_full_uplink_rate_edited_2.csv"
df = pd.read_csv(filename)
df.columns = ["Uplink Rate", "Image Processing Time"]
print(df)
df.to_csv(filename, mode='w')
df.plot(x='Uplink Rate', y='Image Processing Time', kind='line', legend=True)
plt.xlabel('Uplink Rate (Mb/s)')
plt.ylabel('Image Processing Time (ms)')
plt.show()
plt.savefig(folder_results + "full_uplink_rate_fig_2.png")
