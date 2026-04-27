import matplotlib.pyplot as plt
import numpy as np

devices = ['Raspberry Pi 5', 'Jetson Orin Nano', 'Acemagic S1']
weights = [46, 174, 391.2]
power = [6, 10, 25]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

ax1.bar(devices, weights, color=['steelblue', 'darkorange', 'seagreen'])
ax1.bar(devices, weights, color=['steelblue', 'darkorange', 'seagreen'])
ax1.set_ylabel('Weight (grams)')
ax1.set_title('Device Weight Comparison')

ax2.bar(devices, power, color=['steelblue', 'darkorange', 'seagreen'])
ax2.set_ylabel('Power Consumption (W)')
ax2.set_title('Power Consumption Comparison')

plt.tight_layout()
plt.savefig('weight_power_comparison.png', dpi=150)
plt.close()
print("Created weight_power_comparison.png")