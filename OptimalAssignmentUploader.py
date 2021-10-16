import streamlit as st 
import numpy as np 
import pandas as pd 
import scipy.optimize as opt
import altair as alt 

st.title("Optimal Assignment Application")

# INTRO TO THE ASSIGNMENT OPTIMIZATION PROBLEM INSIDE AN EXPANDER CONTAINER
exp1 = st.expander(label="Intro to the Assignment Optimization Problem")

exp1.write(''' 
* The **assignment problem** deals with optimally assigning or pairing of objects of 
two distinct sets (e.g. workers and jobs) where each pairing is associated with some 
cost or benefit. 
* This problem is a **network problem**, but it can also be formulated as an **integer 
linear problem** (i.e. the solutions must be integer). 
''') 

exp1.image("AssignmentProblem.jpg")
exp1.latex(r''' 
Coefficient\_Matrix ( c_{i,j} \ ) \ \Leftrightarrow Weighted\_Bipartite\_Graph
''')

exp1.write('''
* Furthermore, it can be proven that **a network problem with integer constraint 
data (e.g. supplies, demands, capacities), always has integer optimal solutions!** 
* Therefore, the assignment optimization problem can be formulated as a linear problem 
(i.e. dropping the integrality requirement) because we know the optimal solution will 
be integer.

''')

exp1.write('''*  **General Formulation of the Linear Assignment Problem** ''')
exp1.latex(r'''
\min / \max f(\overrightarrow{X}) = \sum_i \sum_j c_{i,j}*x_{i,j}
''')
exp1.latex(r''' 
s.t. \sum_j X_{i,j}=1 \ \forall \ i \  (Each \ staff \ is \ assigned \ to \ one \ role)
''')
exp1.latex(r'''
\ \ \ \ \sum_i X_{i,j}=1 \ \forall \ j \ (Each \ role \ is \ assigned \ to \ one \ task) 
''')
exp1.latex(r'''
 \ \ \ \ x_{i,j} \ \in \{0,1\} \ \ \ \ OR \ \ \ \ x_{i,j} \ \geq 0 \ \ when \ formulated \ as \ a \ linear \ problem
''')

exp1.write(''' 
* The assignment problem can also be solved even more efficiently with the **Hungarian 
algorithm**, a combinatorial optimization algorithm, which takes advantages of the specific 
charasteristics of the problem. 
* The **Hungarian Algorithm** is available in the Python module **`SciPy`** in the sub-module 
**`optimize`**, named the **`linear_sum_assignment`** method (reference [**here**]
(https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)).
* There only data we need to provide to the method is the coefficient matrix.
''')

# INSTRUCTIONS ON HOW TO RUN THE APPLICATION
exp2 = st.expander(label="Instructions on how to run the application")

exp2.write('''**To run the algorithm:**''')

exp2.write('''
* Upload below a workbook containing the coefficient matrix. The workbook can have any name, 
but the worksheet that has the coefficients must be named "Coefficients". 
* The worksheet must have a table with first column named "Coefficients", people's names along the rows, and role 
names along the columns. 
* In the table should be the preference rank for each person for each role, with 1 their first preference, 2 their second, etc. 
* The image below is a generic
layour of a coefficient matrix with 14 staff and roles. 
* Once the file us uploaded, pressthe **"Run Algorithm"** button. 
''')

exp2.image("CoefficientMatrixExample.jpg")

file = st.file_uploader("Upload Assignment Coefficient Matrix Workbook", type="xlsx")

@st.cache() # Decorator
def read_excel_data(workbook, worksheet):
    data = pd.read_excel(workbook, worksheet)
    data.set_index("Coefficients", inplace=True)
    return data

GoButton = st.button("Run Algorithm")

if GoButton: 
    Coefficients = read_excel_data(workbook=file, 
                               worksheet='Coefficients')

    st.dataframe(data=Coefficients, width=650, height=120)

    # Convert Coefficients DataFrame to Numpy Matrix to use in Scipy.Optimize 
    C = Coefficients.values

    # Now we can solve the assignment problem using the Hungarian Algorithm, through the
    # linear_sum_assignment method.

    # row_ind and col_ind are the correcsponding indeces of the optimal solution that are 
    # returned by the method

    row_ind, col_ind = opt.linear_sum_assignment(cost_matrix=C, maximize=False)

    # Since indices start at zero, we add one to the `row_ind` and `col_ind` respectively
    # We can also use the `row_ind` and `col_ind` indices to get the coefficient matrix 
    # values of the optimal allocation
    # We use these to create a table with the optimal allocation and preference, as well as 
    # return the value of the optimal solution

    Solution = pd.concat([pd.DataFrame(data=row_ind, columns=["Staff"]) + 1, 
                        pd.DataFrame(data=col_ind, columns=["Roles"]) + 1, 
                        pd.DataFrame(data=C[row_ind, col_ind], 
                                   columns=["Preference"])], 
                        axis=1)

    ObjectiveValue = C[row_ind, col_ind].sum()
    MaxPreference = Solution["Preference"].max()

    # Define two columns in the Streamlit Layout to place table and greaph next to eachother
    col1, col2 = st.columns(2)

    col1.write("**Optimal Allocation**")
    col1.write(f'''The objective value is **{ObjectiveValue}** and the lowest allocated 
               preference is **{MaxPreference}**.''')
    col1.dataframe(data=Solution,width=280, height=250)

    #f"Last night, {player} scored {points} points."

    PrefBars = alt.Chart(Solution).mark_bar().encode(
        x=alt.X("Preference:Q", bin=alt.Bin(step=1, extent=[1, 14]), title="Preference"), 
        y=alt.Y("count(Preference):Q", axis=None, title="Count")
        ).properties(width=310)
    
    PrefText = PrefBars.mark_text(
        align = "left", 
        baseline = "middle", 
        dy=-7, dx=-2).encode(text="count(Preference):Q")
    
    PrefGraph = PrefBars + PrefText    

    col2.write("**Optimal Preference Distribution**")
    col2.write(" ")
    col2.write(" ")
    col2.write(PrefGraph)