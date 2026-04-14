import matplotlib.pyplot as plt
import numpy as np

# Graph 4: Research Timeline (simple Gantt-style)
fig, ax = plt.subplots(figsize=(10, 4))

tasks = ['Literature Review', 'Jetson Nano\nDevelopment', 'x86 Migration\nDecision', 'SOTA\nValidation', 'Attack\nImplementation']
starts = [0, 4, 14, 16, 18]
durations = [4, 10, 2, 2, 6]

colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']

for i, (task, start, dur, color) in enumerate(zip(tasks, starts, durations, colors)):
    ax.barh(task, dur, left=start, height=0.5, color=color, edgecolor='black', alpha=0.8)

ax.set_xlabel('Weeks', fontsize=12)
ax.set_title('Research Timeline: Jetson → x86 Pivot', fontsize=13, fontweight='bold')
ax.set_xlim(0, 24)
ax.set_xticks(range(0, 25, 4))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.3)

# Mark the pivot point
ax.axvline(x=14, color='red', linestyle='--', linewidth=2, label='Pivot Point')
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig('graph4_research_timeline.png', dpi=150, bbox_inches='tight')
plt.close()
print("Graph 4 saved: graph4_research_timeline.png")
