import matplotlib.pyplot as plt
import numpy as np

# Graph 2: USB Power State Timeline (Jetson vs x86)
fig, ax = plt.subplots(figsize=(10, 4))

time = np.linspace(0, 100, 500)

# Jetson power states (showing SC7 transitions)
jetson_power = np.zeros_like(time)
sc7_events = [20, 45, 70, 90]
for i, t in enumerate(time):
    for sc7 in sc7_events:
        if abs(t - sc7) < 3:
            jetson_power[i] = 0.2
        elif t > sc7 + 3 and t < sc7 + 8:
            jetson_power[i] = 1.0
        elif t > sc7 + 8 and t < sc7 + 15:
            jetson_power[i] = 0.4
    if i > 0 and jetson_power[i] == 0:
        prev = jetson_power[i-1]
        if prev > 0.3:
            jetson_power[i] = 0.4
        else:
            jetson_power[i] = 0.8

# x86 stable power (no SC7)
x86_power = np.ones_like(time) * 0.9

ax.fill_between(time, jetson_power, alpha=0.5, color='#e74c3c', label='Jetson Nano (SC7 transitions)')
ax.fill_between(time, x86_power, alpha=0.5, color='#27ae60', label='x86 NUC (stable)')

ax.set_xlabel('Time (seconds)', fontsize=12)
ax.set_ylabel('USB Power State', fontsize=12)
ax.set_title('USB Power State: Jetson Nano vs x86 over Time', fontsize=13, fontweight='bold')
ax.set_yticks([0.2, 0.5, 0.9])
ax.set_yticklabels(['SC7 Sleep\n(USB Suspended)', 'Resume\n(Transient)', 'Active\n(Stable)'])
ax.set_xlim(0, 100)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

# Mark SC7 events
for sc7 in sc7_events:
    ax.axvline(x=sc7, color='#c0392b', linestyle='--', alpha=0.7, linewidth=1)

plt.tight_layout()
plt.savefig('graph2_usb_power_timeline.png', dpi=150, bbox_inches='tight')
plt.close()
print("Graph 2 saved: graph2_usb_power_timeline.png")
