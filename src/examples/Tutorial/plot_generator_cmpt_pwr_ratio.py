import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
filename = folder_results + "sim_trace_full_edge_cmpt_ratio_fast_uplink_edited_2.csv"
df = pd.read_csv(filename)
df.columns = ["Edge/Drone Compute Power Ratio", "Image Processing Time"]
print(df)
df.to_csv(filename, mode='w')
df.plot(x='Edge/Drone Compute Power Ratio', y='Image Processing Time', kind='line', legend=False)
plt.title("Uplink = 800 Mb/s, Downlink = 6400 Mb/s")
plt.xlabel('Edge/Drone Compute Power Ratio')
plt.ylabel('Image Processing Time (ms)')
plt.show()
plt.savefig(folder_results + "edge_drone_cmpt_pwr_ratio_fast_uplink.png")
