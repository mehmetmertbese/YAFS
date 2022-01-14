import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
filename_full = folder_results + "sim_trace_full_r4_n20_full_uplink_rate_edited_2.csv"
filename_partial = folder_results + "sim_trace_full_r4_n20_partial_uplink_rate_edited_2.csv"
filename_onboard = folder_results + "sim_trace_full_r4_n20_onboard_uplink_rate_edited_2.csv"
df_full = pd.read_csv(filename_full)
df_partial = pd.read_csv(filename_partial)
df_onboard = pd.read_csv(filename_onboard)
#df_full.columns = ["Uplink Rate", "Image Processing Time"]
#df_partial.columns = ["Uplink Rate", "Image Processing Time"]
#df_onboard.columns = ["Uplink Rate", "Image Processing Time"]
#print(df_full)
#df_full.to_csv(filename_full, mode='w')
#df_partial.to_csv(filename_partial, mode='w')
#df_onboard.to_csv(filename_onboard, mode='w')
ax = df_full.plot(x='Uplink Rate', y='Image Processing Time', kind='line', legend=True, label = "full")
df_partial.plot(x='Uplink Rate', y='Image Processing Time', kind='line', legend=True, label = "partial", ax=ax)
df_onboard.plot(x='Uplink Rate', y='Image Processing Time', kind='line', legend=True, label = "onboard", ax = ax)
ax.legend()
ax.set_yscale('log')
plt.xlabel('Uplink Rate (Mb/s)')
plt.ylabel('Image Processing Time (ms)')
plt.show()
plt.savefig(folder_results + "combined_uplink_rate_fig.png")
