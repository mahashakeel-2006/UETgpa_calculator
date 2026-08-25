import pandas as pd
import matplotlib.pyplot as plt

# 1. Define the official UET Lahore grading scale mapping
UET_GRADES = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 
    'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7, 
    'D+': 1.3, 'D': 1.0, 'F': 0.0
}

# 2. Structured core data sample representing engineering course tracking
data = {
    'Semester': ['1st', '1st', '1st', '2nd', '2nd', '2nd'],
    'Course_Code': ['CS-111', 'MA-113', 'HU-111', 'CS-112', 'EE-114', 'MA-123'],
    'Credit_Hours': [3.0, 3.0, 2.0, 4.0, 3.0, 3.0],
    'Letter_Grade': ['A', 'B+', 'A-', 'B', 'C+', 'A']
}

# 3. Initialize structured multi-column dataset
df = pd.DataFrame(data)

# 4. Map strings cleanly to evaluation floats via Vector Layer dictionary keys
df['Grade_Points'] = df['Letter_Grade'].map(UET_GRADES)

# 5. Multiply individual grade marks element-wise against registered workloads
df['Quality_Points'] = df['Grade_Points'] * df['Credit_Hours']

# 6. Global aggregate calculations matching official academic logic matrices
total_credits = df['Credit_Hours'].sum()
total_qp = df['Quality_Points'].sum()
cgpa = total_qp / total_credits

print("\n" + "="*40)
print("     UET LAHORE GPA TERMINAL REPORT     ")
print("="*40)
print(f"Total Registered Credit Hours : {total_credits:.1f}")
print(f"Cumulative Quality Points (QP): {total_qp:.2f}")
print(f"Calculated Overall CGPA       : {cgpa:.2f}")
print("="*40 + "\n")

# 7. Multi-term grouping logic to extract individual semester scores
sem_summary = df.groupby('Semester').apply(
    lambda x: (x['Grade_Points'] * x['Credit_Hours']).sum() / x['Credit_Hours'].sum()
)

print("--- Semester Breakdown Summary ---")
for sem, gpa in sem_summary.items():
    print(f"Semester Term: {sem} | GPA Metric: {gpa:.2f}")
print("-" * 34 + "\n")

# 8. Frame structural visualization curves using Matplotlib
plt.figure(figsize=(6, 4))
plt.plot(sem_summary.index, sem_summary.values, marker='o', color='#004B87', linewidth=2.5, label="GPA Progress")
plt.title('UET Academic GPA Progress Curve', fontsize=11, fontweight='bold')
plt.xlabel('Semester Year Classification')
plt.ylabel('GPA (Max Scale 4.00)')
plt.ylim(0.0, 4.1)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower left')

# 9. Save graphic coordinates as a static file asset inside workspace
plt.savefig('gpa_trend.png', dpi=150, bbox_inches='tight')
print("🎉 Analytics completed successfully! Chart saved as 'gpa_trend.png'.")
