import calendar
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go # We will use this to plot the graph 
from streamlit_option_menu import option_menu # We will use this to create the Menubar/Navbar

import database as db # Now import the database.py file created as db into app.py

# Declaring all variables, lists and settings to be used.
incomes = ["Salary", "Blog", "Other Income"]
expenses = ["Rent", "Utilities", "Groceries", "Transportation", "Other Expenses", "Savings"]
currency = "NGN"
page_title = "Income and Expenses Tracker"
page_icon = ":money_with_wings:" # for emojis, go to https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered" # We can also set it wide


# Setting up the page config and title
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# Creating a new header and form to hold/display the years and months, as well as the income and expenses for user to choose from
years = [datetime.today().year - 1, datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html= True)

st.sidebar.text("Made With Love by Akindele")

def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

menu_selection = option_menu(
    menu_title = None,
    options = ["Data Entry", "Data Visualization"],
    icons = ["pencil-fill", "bar-chart-fill"], # go to https://icons/bootstrap.com
    orientation = "horizontal" 
)

if menu_selection == "Data Entry":
    st.header(f"Data Entry in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:" , months, key = "month")
        col2.selectbox("Select Year:", years, key = "year")
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value = 0, format= "%i", step = 10, key = income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value = 0, format = "%i", step = 10, key = expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder = "Enter a comment here ...")

        submitted = st.form_submit_button("Save Data")
        # Now, after the user submit, we need to get all the values from the inputted fields so as to submit to the database.
        # We will do this getting the key of each widget which is stored in the current session state of the form
        if submitted:
            # For period(year/month) - We will string and concatenate them using an underscore.    
            period = str(st.session_state["year"])  + "_" + str(st.session_state["month"])
            # For income - We will use dictionary comprehension since we used key value instead of typing out all the incomes.
            incomes = {income: st.session_state[income] for income in incomes}
            # For expense - We will also use dictionary comprehension since we used key value instead of typing out all the expense.
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period, incomes, expenses, comment)
            # Listing out the values before writing them to the database
            st.write(f"incomes: {incomes}")
            st.write(f"expenses: {expenses}")
            st.success("Data saved")

# ----- Data Plotting -----
if menu_selection == "Data Visualization":
    st.header("Data Visualization")
    with st.form("Saved_Periods"):
        period = st.selectbox("Select Period:", get_all_periods()) # We can hardcode ["2022_March"]
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            expenses = period_data.get("expenses")
            incomes = period_data.get("incomes")

            """
            comment = "Some Comment"
            incomes = {'Salary': 1500, 'Blog': 250, 'Other Incomes': 300}
            expenses = {'Rent': 600, 'Utilities': 150, 'Groceries': 110, 'Transportation': 200, 'Other Expenses': 50, 'Savings': 100}
            """
            
            # Create metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{currency} {total_income}")
            col2.metric("Total Expense", f"{currency} {total_expense}")
            col3.metric("Remaining Budget", f"{currency} {remaining_budget}")
            st.text(f"Comment: {comment}")


            # Create sankey Chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses]
            value = list(incomes.values()) + list(expenses.values())

            #  Data to dict, dict to sankey
            link = dict(source = source, target = target, value = value)
            node = dict(label = label, pad = 20, thickness = 30, color = "#E694FF")
            data = go.Sankey(link = link, node = node)

            # Plot the graph
            fig = go.Figure(data)
            fig.update_layout(margin = dict(l = 0, r = 0, t = 5, b = 5))
            st.plotly_chart(fig, use_container_width = True)

# Create a config.toml inside ".streamlit" folder.
# Next is to create a database to store our data and we can make CRUD operations.
# Go to https://wwww.deta.sh and signup for an account and create a database.
# Next install deta module/framework in the terminal: pip3 install deta.
# We may also need to install dotenv: pip3 install python-dotenv.
# Also, create a .gitignore file, and put in all files which not need to be uploaded ongithub: go to gitignore.io, and type in python and click on "create".
# Copy out the content and paste it into the .gitignore file earlier created.

