import matplotlib.pyplot as plt
import numpy as np

# Exact data and style from generate_graphs.py (Graph 2) - Only Translated
time = [0, 1, 2, 3, 4, 5, 6, 7, 8]
voltage = [5, 5, 5, 5, 3, 1.5, 0.5, 0, 0]

fig, ax = plt.subplots(figsize=(7, 4))

ax.plot(time, voltage, 'r-o', linewidth=2.5, markersize=10)

ax.set_ylim(0, 6)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('USB VBUS Voltage (V)')
ax.set_title('Jetson Orin Nano: USB Voltage Drop due to SC7', fontweight='bold', fontsize=11)

ax.text(1, 5.3, '5V', fontsize=10)
ax.text(7.5, 0.3, '0V', fontsize=10)

plt.tight_layout()
plt.savefig('graph2_usb_power_comparison.png', facecolor='white')
plt.close()
print("Created: graph2_usb_power_comparison.png")
