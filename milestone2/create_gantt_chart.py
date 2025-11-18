"""
Create Gantt Charts for Milestone 1 & 2
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import pandas as pd

# Milestone 1 Tasks
milestone1_tasks = [
    {"Task": "Data Collection", "Start": 0, "Duration": 5, "Team": "All"},
    {"Task": "Data Cleaning", "Start": 5, "Duration": 4, "Team": "Backend"},
    {"Task": "Airflow Pipeline Setup", "Start": 9, "Duration": 3, "Team": "DevOps"},
    {"Task": "ChromaDB Integration", "Start": 12, "Duration": 4, "Team": "Backend"},
    {"Task": "Data Validation", "Start": 16, "Duration": 2, "Team": "QA"},
    {"Task": "DVC Setup", "Start": 18, "Duration": 2, "Team": "DevOps"},
    {"Task": "Testing & Documentation", "Start": 20, "Duration": 3, "Team": "All"}
]

# Milestone 2 Tasks
milestone2_tasks = [
    {"Task": "Data Loader", "Start": 0, "Duration": 1, "Team": "Backend"},
    {"Task": "Model Training", "Start": 1, "Duration": 2, "Team": "ML"},
    {"Task": "Hyperparameter Tuning", "Start": 3, "Duration": 3, "Team": "ML"},
    {"Task": "Model Validation", "Start": 6, "Duration": 2, "Team": "QA"},
    {"Task": "Bias Detection", "Start": 8, "Duration": 2, "Team": "ML"},
    {"Task": "Anomaly Detection", "Start": 10, "Duration": 1, "Team": "ML"},
    {"Task": "Experiment Tracking (MLflow)", "Start": 11, "Duration": 1, "Team": "MLOps"},
    {"Task": "SHAP Analysis", "Start": 12, "Duration": 1, "Team": "ML"},
    {"Task": "RAG Pipeline Development", "Start": 13, "Duration": 3, "Team": "Backend"},
    {"Task": "FastAPI Backend", "Start": 16, "Duration": 2, "Team": "Backend"},
    {"Task": "Input Validation & Security", "Start": 18, "Duration": 1, "Team": "Backend"},
    {"Task": "CI/CD Pipeline", "Start": 19, "Duration": 2, "Team": "DevOps"},
    {"Task": "Docker Setup", "Start": 21, "Duration": 1, "Team": "DevOps"},
    {"Task": "GCP Registry Setup", "Start": 22, "Duration": 1, "Team": "DevOps"},
    {"Task": "Testing & Documentation", "Start": 23, "Duration": 2, "Team": "All"}
]

# Color mapping
colors = {
    "All": "#3498db",
    "Backend": "#2ecc71",
    "ML": "#e74c3c",
    "QA": "#f39c12",
    "DevOps": "#9b59b6",
    "MLOps": "#1abc9c"
}

def create_gantt(tasks, title, filename):
    """Create Gantt chart"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot bars
    for idx, task in enumerate(tasks):
        ax.barh(
            idx,
            task["Duration"],
            left=task["Start"],
            height=0.6,
            color=colors[task["Team"]],
            edgecolor='black',
            linewidth=0.5
        )
        
        # Add task name inside bar
        ax.text(
            task["Start"] + task["Duration"]/2,
            idx,
            task["Task"],
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            color='white'
        )
    
    # Labels
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([f"{i+1}. {t['Task']}" for i, t in enumerate(tasks)])
    ax.set_xlabel('Days', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Legend
    legend_elements = [mpatches.Patch(color=color, label=team) 
                      for team, color in colors.items() if team in [t['Team'] for t in tasks]]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")

# Create charts
print("📊 Creating Gantt Charts...")

create_gantt(
    milestone1_tasks,
    "PropBot Milestone 1: Data Pipeline Development",
    "results/gantt_chart_milestone1.png"
)

create_gantt(
    milestone2_tasks,
    "PropBot Milestone 2: ML Model Development & Deployment",
    "results/gantt_chart_milestone2.png"
)

print("\n🎉 Gantt charts created!")
print("   View: results/gantt_chart_milestone1.png")
print("   View: results/gantt_chart_milestone2.png")
