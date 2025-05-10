import streamlit as st
import pandas as pd
import os
import re
from datetime import date

# --- Sidebar Navigation ---
st.sidebar.title("Balsons Heavy Lift & Shift ERP")

# Navigation options
page = st.sidebar.radio("Select a Page", ["Employee Master", "Attendance Muster", "Payroll Information"])

# Define the file path for Employee Master CSV
CSV_FILE = "employee_master_data.csv"

# --- Employee Master Section ---
if page == "Employee Master":
    # Load or initialize employee data
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=[
            'Employee Code', 'EC Number', 'Surname', 'First Name', 'Middle Name', 'Name of Employee',
            'Date of Birth', 'Email ID', 'Joining Date',
            'Bank Name', 'Account Number', 'IFSC Code', 'PF Number (UAN)',
            'Basic Salary', 'DA', 'TA', 'OA', 'LTA', 'HRA', 'PF', 'ESCI', 'Grand Total', 'Employee Status'
        ])

    # Ensure required columns
    if 'Employee Status' not in df.columns:
        df['Employee Status'] = 'Active'

    # --- Branding and Header ---
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("C:/Users/Tasma/Downloads/BS.jpeg", width=100)
    with col_title:
        st.markdown("""
            <h2 style='margin-bottom:0;'>👷‍♂️ Balsons Heavy Lift & Shift</h2>
            <p style='margin-top:0; color:gray;'>Employee Master Data System | <a href='https://balsonsheavylift.com' target='_blank'>Visit Company Website</a></p>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Dashboard Section ---
    st.markdown("### 📊 Dashboard Summary")

    active_count = df[df['Employee Status'] == 'Active'].shape[0]
    probation_count = df[df['Employee Status'] == 'Probation'].shape[0]
    resigned_count = df[df['Employee Status'] == 'Resigned'].shape[0]
    total_payment = df['Grand Total'].sum()

    d1, d2, d3, d4 = st.columns([1, 1, 1, 2])
    d1.metric("👥 Active Employees", active_count)
    d2.metric("🕒 On Probation", probation_count)
    d3.metric("📤 Resigned", resigned_count)
    d4.metric("💰 Total Payment Value", f"₹ {total_payment:,.2f}")

    st.markdown("---")

    # --- Sidebar Upload ---
    st.sidebar.header("📤 Upload Employee Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded_file:
        uploaded_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        if 'Employee Status' not in uploaded_df.columns:
            uploaded_df['Employee Status'] = 'Active'
        df = pd.concat([df, uploaded_df], ignore_index=True).drop_duplicates(subset=["EC Number"])
        df.to_csv(CSV_FILE, index=False)
        st.sidebar.success("✅ Data uploaded successfully!")

    # --- State Setup ---
    st.session_state.setdefault("show_form", False)
    st.session_state.setdefault("show_edit_form", False)
    st.session_state.setdefault("selected_employee", None)

    # --- Buttons for Add/Edit ---
    col1, col2 = st.columns(2)
    if col1.button("➕ Add New Employee"):
        st.session_state["show_form"] = True
        st.session_state["show_edit_form"] = False
        st.session_state["selected_employee"] = None
    if col2.button("✏️ Edit Existing Employee"):
        st.session_state["show_form"] = False
        st.session_state["show_edit_form"] = True
        st.session_state["selected_employee"] = None

    # --- EC Generator ---
    def get_next_ec(existing_ecs):
        if existing_ecs.empty:
            return "EC001"
        nums = [int(re.sub(r'\D', '', ec)) for ec in existing_ecs if re.sub(r'\D', '', ec).isdigit()]
        return f"EC{max(nums) + 1:03d}"

    # --- Add New Employee ---
    if st.session_state["show_form"]:
        with st.form("employee_form", clear_on_submit=True):
            st.subheader("🧑 Employee Details")
            emp_code = st.text_input("Employee Code").strip().upper()
            surname = st.text_input("Surname").strip().upper()
            first_name = st.text_input("First Name").strip().upper()
            middle_name = st.text_input("Middle Name").strip().upper()
            full_name = f"{surname} {first_name} {middle_name}".strip()
            dob = st.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())
            email = st.text_input("Email ID").strip()
            joining_date = st.date_input("Joining Date", min_value=date(2000, 1, 1), max_value=date.today())

            ec_number = get_next_ec(df['EC Number'])

            st.subheader("🏦 Bank Details")
            bank_name = st.text_input("Bank Name")
            account_number = st.text_input("Account Number")
            ifsc_code = st.text_input("IFSC Code")
            pf_number = st.text_input("PF Number (UAN)")

            st.subheader("💸 Salary Details")
            basic = st.number_input("Basic Salary", min_value=0.0, step=100.0, format="%.2f")
            da, ta, oa, lta, hra, pf_amt, esci = [basic * x for x in [0.5, 0.2, 0.2, 0.0833, 0.5, 0.24, 0.0325]]
            grand_total = basic + da + ta + oa + lta + hra + pf_amt + esci if basic > 0 else 0.0

            employee_status = st.selectbox("Employee Status", ["Active", "Probation", "Resigned", "Retired", "Inactive"])

            submitted = st.form_submit_button("✅ Save Employee")
            if submitted:
                new_row = pd.DataFrame([{
                    'Employee Code': emp_code, 'EC Number': ec_number, 'Surname': surname,
                    'First Name': first_name, 'Middle Name': middle_name, 'Name of Employee': full_name,
                    'Date of Birth': dob, 'Email ID': email, 'Joining Date': joining_date,
                    'Bank Name': bank_name, 'Account Number': account_number, 'IFSC Code': ifsc_code, 'PF Number (UAN)': pf_number,
                    'Basic Salary': basic, 'DA': da, 'TA': ta, 'OA': oa, 'LTA': lta, 'HRA': hra, 'PF': pf_amt, 'ESCI': esci,
                    'Grand Total': grand_total, 'Employee Status': employee_status
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success("✅ Employee added successfully!")
                st.session_state["show_form"] = False

    # --- Edit Employee Form ---
    if st.session_state["show_edit_form"]:
        st.subheader("🔄 Edit Employee Details")

        if df.empty:
            st.warning("No employee records found to edit.")
        else:
            ec_numbers = df['EC Number'].unique()
            selected_ec = st.selectbox("Select Employee by EC Number", ec_numbers, key="edit_selectbox")

            if selected_ec:
                selected_employee = df[df['EC Number'] == selected_ec].iloc[0]
                st.session_state.selected_employee = selected_employee

                with st.form("edit_employee_form"):
                    surname = st.text_input("Surname", value=selected_employee['Surname'])
                    first_name = st.text_input("First Name", value=selected_employee['First Name'])
                    middle_name = st.text_input("Middle Name", value=selected_employee['Middle Name'])
                    full_name = f"{surname} {first_name} {middle_name}".strip()

                    basic = st.number_input("Basic Salary", value=float(selected_employee['Basic Salary']), min_value=0.0, step=100.0, format="%.2f")
                    dob = st.date_input("Date of Birth", value=pd.to_datetime(selected_employee['Date of Birth'], errors='coerce').date() if pd.notna(selected_employee['Date of Birth']) else date(2000, 1, 1))
                    joining_date = st.date_input("Joining Date", value=pd.to_datetime(selected_employee['Joining Date'], errors='coerce').date() if pd.notna(selected_employee['Joining Date']) else date.today())
                    employee_status = st.selectbox("Employee Status", ["Active", "Probation", "Resigned", "Retired", "Inactive"],
                                                   index=["Active", "Probation", "Resigned", "Retired", "Inactive"].index(selected_employee['Employee Status']))

                    # Recalculate salary components
                    da = basic * 0.5
                    ta = basic * 0.2
                    oa = basic * 0.2
                    lta = basic * 0.0833
                    hra = basic * 0.5
                    pf_amt = basic * 0.24
                    esci = basic * 0.0325
                    grand_total = basic + da + ta + oa + lta + hra + pf_amt + esci

                    update_submitted = st.form_submit_button("✅ Update Employee")
                    if update_submitted:
                        df.loc[df['EC Number'] == selected_ec, [
                            'Surname', 'First Name', 'Middle Name', 'Name of Employee',
                            'Date of Birth', 'Joining Date', 'Basic Salary',
                            'DA', 'TA', 'OA', 'LTA', 'HRA', 'PF', 'ESCI', 'Grand Total',
                            'Employee Status'
                        ]] = [
                            surname, first_name, middle_name, full_name,
                            dob, joining_date, basic,
                            da, ta, oa, lta, hra, pf_amt, esci, grand_total,
                            employee_status
                        ]
                        df.to_csv(CSV_FILE, index=False)
                        st.success(f"✅ Employee {selected_ec} updated successfully!")

    # --- Show Data Table ---
    st.subheader("📋 Employee Master Data")
    st.dataframe(df, use_container_width=True)

    # --- Delete Section ---
    with st.expander("🗑️ Delete Employee"):
        if not df.empty:
            ec_to_delete = st.selectbox("Select EC Number to delete", df['EC Number'].unique())
            if st.button("Delete"):
                df = df[df['EC Number'] != ec_to_delete]
                df.to_csv(CSV_FILE, index=False)
                st.warning(f"⚠️ Employee {ec_to_delete} deleted.")
        else:
            st.info("No records available to delete.")

# --- Attendance Muster Section ---
elif page == "Attendance Muster":
    st.write("Attendance Muster page is under construction.")

# --- Payroll Information Section ---
elif page == "Payroll Information":
    st.write("Payroll Information page is under construction.")
