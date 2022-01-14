import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
filename_fast_uplink = folder_results + "sim_trace_full_edge_cmpt_ratio_fast_uplink_edited_2.csv"
filename_uplink = folder_results + "sim_trace_full_edge_cmpt_ratio_edited_2.csv"
df_fast = pd.read_csv(filename_fast_uplink)
df_uplink = pd.read_csv(filename_uplink)
# df.columns = ["Edge/Drone Compute Power Ratio", "Image Processing Time"]
# print(df)
# df.to_csv(filename_fast_uplink, mode='w')
ax = df_fast.plot(x='Edge/Drone Compute Power Ratio', y='Image Processing Time', kind='line', legend=True,
                  label="Uplink = 800 Mb/s, Downlink = 6400 Mb/s")
df_uplink.plot(x='Edge/Drone Compute Power Ratio', y='Image Processing Time', kind='line',
               legend=True, label="Uplink = 100 Mb/s, Downlink 800 Mb/s", ax=ax)
plt.title("Full Offloading")
ax.set_yscale('log')
plt.xlabel('Edge/Drone Compute Power Ratio')
plt.ylabel('Image Processing Time (ms)')
plt.show()
plt.savefig(folder_results + "edge_drone_cmpt_pwr_ratio_uplink_combined_2.png")
