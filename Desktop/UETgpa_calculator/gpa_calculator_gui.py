import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Official UET Lahore Grade Configurations Matrices
UET_GRADES = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 
    'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7, 
    'D+': 1.3, 'D': 1.0, 'F': 0.0
}

class UETGpaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UET Lahore GPA/CGPA Dashboard")
        self.root.geometry("950x620")
        
        # In-memory storage for course entry logs
        self.courses = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Configure weight for root window grid to allow responsive resizing
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- Left Input Panel Frame Layout ---
        input_frame = ttk.LabelFrame(self.root, text=" Course Management Module ", padding=15)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        
        # Configure internal grid columns to stretch properly
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=2)
        
        ttk.Label(input_frame, text="Semester:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=5)
        self.sem_var = ttk.Combobox(input_frame, values=["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], width=18, state="readonly")
        self.sem_var.grid(row=0, column=1, pady=8, padx=5, sticky=tk.EW)
        self.sem_var.current(0)
        
        ttk.Label(input_frame, text="Course Code:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=5)
        self.code_var = ttk.Entry(input_frame, width=20)
        self.code_var.grid(row=1, column=1, pady=8, padx=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Credit Hours:").grid(row=2, column=0, sticky=tk.W, pady=8, padx=5)
        self.credit_var = tk.DoubleVar(value=3.0)  # Corrected tk module namespace target reference
        self.credit_spin = ttk.Spinbox(input_frame, from_=1.0, to=4.0, increment=0.5, textvariable=self.credit_var, width=18)
        self.credit_spin.grid(row=2, column=1, pady=8, padx=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Letter Grade:").grid(row=3, column=0, sticky=tk.W, pady=8, padx=5)
        self.grade_var = ttk.Combobox(input_frame, values=list(UET_GRADES.keys()), width=18, state="readonly")
        self.grade_var.grid(row=3, column=1, pady=8, padx=5, sticky=tk.EW)
        self.grade_var.current(0)
        
        btn_add = ttk.Button(input_frame, text="Add Course Entry", command=self.add_course)
        btn_add.grid(row=4, column=0, columnspan=2, pady=20, padx=5, sticky=tk.EW)
        
        # Display Summary Dashboard Core Metrics Panel with better padding
        self.lbl_cgpa = ttk.Label(input_frame, text="Overall CGPA: 0.00", font=("Arial", 13, "bold"), foreground="#004B87")
        self.lbl_cgpa.grid(row=5, column=0, columnspan=2, pady=8)
        
        self.lbl_credits = ttk.Label(input_frame, text="Total Credits: 0.0", font=("Arial", 11))
        self.lbl_credits.grid(row=6, column=0, columnspan=2, pady=5)

        btn_clear = ttk.Button(input_frame, text="Clear Data Log", command=self.clear_data)
        btn_clear.grid(row=7, column=0, columnspan=2, pady=20, padx=5, sticky=tk.EW)

        # --- Right Visualization & Output Frame Layout ---
        self.right_frame = ttk.Frame(self.root, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview Tabular Component View
        self.tree = ttk.Treeview(self.right_frame, columns=("Sem", "Code", "Credits", "Grade"), show='headings', height=8)
        self.tree.heading("Sem", text="Semester")
        self.tree.heading("Code", text="Course Code")
        self.tree.heading("Credits", text="Credit Hours")
        self.tree.heading("Grade", text="Grade")
        self.tree.column("Sem", width=100, anchor=tk.CENTER)
        self.tree.column("Code", width=140, anchor=tk.CENTER)
        self.tree.column("Credits", width=120, anchor=tk.CENTER)
        self.tree.column("Grade", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, pady=10)

        # Matplotlib Canvas Frame Layer Rendering Placeholder Area
        self.plot_frame = ttk.Frame(self.right_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)


    def add_course(self):
        code = self.code_var.get().strip().upper()
        if not code:
            messagebox.showwarning("Missing Data", "Please input a valid Course Code.")
            return
            
        self.courses.append({
            "Semester": self.sem_var.get(),
            "Course_Code": code,
            "Credit_Hours": float(self.credit_var.get()),
            "Letter_Grade": self.grade_var.get()
        })
        
        self.tree.insert("", tk.END, values=(self.sem_var.get(), code, self.credit_var.get(), self.grade_var.get()))
        self.code_var.delete(0, tk.END)
        self.recalculate_analytics()

    def clear_data(self):
        self.courses.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.lbl_cgpa.config(text="Overall CGPA: 0.00")
        self.lbl_credits.config(text="Total Credits: 0.0")

    def recalculate_analytics(self):
        if not self.courses:
            return
            
        # Parse inputs natively into Pandas Data Engine Vector Layer
        df = pd.DataFrame(self.courses)
        df['Grade_Points'] = df['Letter_Grade'].map(UET_GRADES)
        df['Quality_Points'] = df['Grade_Points'] * df['Credit_Hours']
        
        total_credits = df['Credit_Hours'].sum()
        total_qp = df['Quality_Points'].sum()
        cgpa = total_qp / total_credits if total_credits > 0 else 0.0
        
        self.lbl_cgpa.config(text=f"Overall CGPA: {cgpa:.2f}")
        self.lbl_credits.config(text=f"Total Credits: {total_credits:.1f}")
        
        # Chronological Multi-Term Mapping Group Execution 
        sem_summary = df.groupby('Semester').apply(
            lambda x: (x['Grade_Points'] * x['Credit_Hours']).sum() / x['Credit_Hours'].sum()
        )
        
        # Clear prior iteration visualization layers
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        # Build new Matplotlib Embedded Figure Canvas Frame Object
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(sem_summary.index, sem_summary.values, marker='o', color='#004B87', linewidth=2.5)
        ax.set_title("UET Academic GPA Progress Curve", fontsize=10, fontweight='bold')
        ax.set_xlabel("Semester Term Tracking Node")
        ax.set_ylabel("GPA Scale Range")
        ax.set_ylim(0.0, 4.1)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Inject Matplotlib chart inside Tkinter frame container
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

if __name__ == "__main__":
    window = tk.Tk()
    app = UETGpaApp(window)
    window.mainloop()
