import streamlit as st
import pandas as pd
import numpy as np
import gspread
import plotly.express as px
from datetime import datetime
import os
import json

# --- PAGE SETUP & CUSTOM CSS ---
st.set_page_config(page_title="Inventory Insights - SSR 1.6", page_icon="📦", layout="wide")

st.markdown("""
<style>
    /* 1. Force the Sidebar Background Color */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #e6ebf1 !important;
    }
    
    /* 2. Make the text inside the sidebar a matching dark blue */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h3 {
        color: #0F4C81 !important;
    }

    /* 3. Custom Header Banner (For Dashboard) */
    .main-banner {
        background: linear-gradient(135deg, #0F4C81, #1E3A8A); 
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .main-banner h1 {
        color: white !important;
        margin: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.4rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# --- 0. AUTHENTICATION (LOGIN PAGE) ---
# ==========================================

# Hardcoded Users (Username : Password)
USER_CREDENTIALS = {
    "admin": "watermelon2026",
    "warehouse": "stock2024"
}

# Initialize session state for login status
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# If the user is NOT logged in, show the styled login form
if not st.session_state["authenticated"]:
    
    # ✨ NEW: Login-Page Only CSS
    st.markdown("""
    <style>
        /* 1. Deep blue gradient background for the whole page */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0a2e4f 0%, #0F4C81 100%);
            background-size: cover;
        }
        
        /* 2. Hide the sidebar completely on the login page */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* 3. Make the default top header transparent */
        [data-testid="stHeader"] {
            background-color: transparent;
        }
        
        /* 4. Style the login form box so it pops and floats */
        div[data-testid="stForm"] {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add vertical space to push the login box down to the middle
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Use columns to center the login box perfectly
    col1, col2, col3 = st.columns([1, 1.2, 1]) 
    
    with col2:
        # Professional Header for Login
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='color: white; font-family: sans-serif; margin-bottom: 0;'>📦 Inventory Insights</h1>
            <h3 style='color: #c3cfe2; font-family: sans-serif; margin-top: 0; font-weight: 300;'>MFM</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # The Login Form
        with st.form("login_form", clear_on_submit=True):
            st.markdown("<h4 style='text-align: center; color: #333;'>Sign In to Continue</h4>", unsafe_allow_html=True)
            st.write("") # slight padding
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.write("") # slight padding
            submit_button = st.form_submit_button("Secure Login ➔", use_container_width=True)
            
            if submit_button:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state["authenticated"] = True
                    st.rerun() # Refresh the page to load the dashboard!
                else:
                    st.error("❌ Invalid username or password. Please try again.")
    
    # STOP EXECUTION HERE! Do not load data or render the rest of the app if not logged in.
    st.stop()


# ==========================================
# --- DASHBOARD STARTS HERE ---
# ==========================================
# This banner only prints AFTER they successfully log in!
st.markdown("""
<div class="main-banner">
    <h1>📦 Nexus Inventory Command</h1>
</div>
""", unsafe_allow_html=True)


# Add a logout button to the sidebar
with st.sidebar:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    st.write("---")


# --- 1. CONNECT & LOAD DATA ---
@st.cache_data(ttl=600)
def load_data():
    client = None
    
# ... (THE REST OF YOUR EXISTING CODE REMAINS EXACTLY THE SAME FROM HERE DOWN) ...

# --- 1. CONNECT & LOAD DATA ---
@st.cache_data(ttl=600)
def load_data():
    import os
    import json
    import gspread
    import streamlit as st
    
    client = None
    
    # 1. STREAMLIT CLOUD: Try to read from Streamlit's TOML secrets
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            client = gspread.service_account_from_dict(creds_dict)
    except Exception:
        pass # If st.secrets doesn't exist, silently ignore and move on
        
    # If Streamlit Cloud didn't work, try the next options:
    if client is None:
        try:
            # 2. HUGGING FACE: Try to read from Hugging Face's Environment Variables
            if "gcp_service_account" in os.environ:
                creds_dict = json.loads(os.environ["gcp_service_account"])
                client = gspread.service_account_from_dict(creds_dict)
                
            # 3. LOCAL MAC: Fallback to reading the physical file on your computer
            else:
                client = gspread.service_account(filename="credentials.json")
        except Exception as e:
            raise Exception(f"Failed to load credentials: {e}")
            
    try:        
        sheet = client.open("stock_input") 
        df_open = pd.DataFrame(sheet.worksheet("OpeningBalance").get_all_records())
        df_rec = pd.DataFrame(sheet.worksheet("Received").get_all_records())
        df_iss = pd.DataFrame(sheet.worksheet("Issued").get_all_records())
        return df_open, df_rec, df_iss
    except Exception as e:
        raise Exception(f"Failed to open Google Sheet data: {e}")

try:
    with st.spinner("Connecting to Google Sheets securely..."):
        df_open, df_rec, df_iss = load_data()
except Exception as e:
    st.error(f"Connection Failed: {e}")
    st.stop()

# --- 2. DATA CLEANING & DICTIONARIES ---
for df in [df_open, df_rec, df_iss]:
    if 'BatchNumber' in df.columns: df['BatchNumber'] = df['BatchNumber'].astype(str).str.strip()
    if 'ItemCode' in df.columns: df['ItemCode'] = df['ItemCode'].astype(str).str.strip()
    if 'ItemDescription' in df.columns: df['ItemDescription'] = df['ItemDescription'].astype(str).str.strip()
    if 'ExpiryDate' in df.columns:
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], errors='coerce').dt.strftime('%Y-%m')
        df['ExpiryDate'] = df['ExpiryDate'].fillna('Unknown')

df_rec['ReceivedDate'] = pd.to_datetime(df_rec['ReceivedDate'], errors='coerce')
df_iss['IssuedDate'] = pd.to_datetime(df_iss['IssuedDate'], errors='coerce')
if 'ReceivedbyFacility' in df_iss.columns: df_iss['ReceivedbyFacility'] = pd.to_datetime(df_iss['ReceivedbyFacility'], errors='coerce')

df_open['Balance'] = pd.to_numeric(df_open['Balance'], errors='coerce').fillna(0)
df_rec['ReceivedQuantity'] = pd.to_numeric(df_rec['ReceivedQuantity'], errors='coerce').fillna(0)
df_iss['IssuedQuantity'] = pd.to_numeric(df_iss['IssuedQuantity'], errors='coerce').fillna(0)

desc_mapping = pd.concat([
    df_open[['ItemCode', 'ItemDescription']] if 'ItemDescription' in df_open.columns else pd.DataFrame(),
    df_rec[['ItemCode', 'ItemDescription']] if 'ItemDescription' in df_rec.columns else pd.DataFrame(),
    df_iss[['ItemCode', 'ItemDescription']] if 'ItemDescription' in df_iss.columns else pd.DataFrame()
]).dropna().drop_duplicates(subset=['ItemCode']).set_index('ItemCode')['ItemDescription'].to_dict()


# --- 3. SIDEBAR: UNIVERSAL FILTERS ---
st.sidebar.header("Parameters & Filters")

min_date, max_date = pd.to_datetime('2025-12-31').date(), pd.Timestamp.today().date()
if not df_rec.empty or not df_iss.empty:
    all_dates = pd.concat([df_rec['ReceivedDate'], df_iss['IssuedDate']]).dropna()
    if not all_dates.empty: min_date, max_date = all_dates.min().date(), all_dates.max().date()

date_selection = st.sidebar.date_input("Select Reporting Period", [min_date, max_date])
start_date, end_date = date_selection if len(date_selection) == 2 else (date_selection[0], date_selection[0])
start_dt, end_dt = pd.to_datetime(start_date), pd.to_datetime(end_date)

st.sidebar.markdown("### Stock Level Policy (Months)")
min_stock = st.sidebar.number_input("Minimum Stock Level (Buffer)", min_value=0.0, value=3.0, step=0.5)
reorder_interval = st.sidebar.number_input("Re-order Interval", min_value=1.0, value=6.0, step=0.5)
max_stock = min_stock + reorder_interval
st.sidebar.info(f"💡 **Calculated Max Stock: {max_stock} Months**\n\n*(Min + Re-order Interval)*")

amc_window = st.sidebar.selectbox("Rolling AMC Window (Months)", options=[3, 6, 9, 12], index=0)

all_items_list = sorted(list(set(df_open['ItemCode'].unique()) | set(df_rec['ItemCode'].unique()) | set(df_iss['ItemCode'].unique())))
selected_item = st.sidebar.selectbox("Select Item", options=["All Items"] + all_items_list, format_func=lambda c: "All Items" if c == "All Items" else f"{c} - {desc_mapping.get(c, 'Unknown')}", index=0)

if selected_item == "All Items":
    i_open, i_rec, i_iss = df_open.copy(), df_rec.copy(), df_iss.copy()
else:
    i_open, i_rec, i_iss = df_open[df_open['ItemCode'] == selected_item].copy(), df_rec[df_rec['ItemCode'] == selected_item].copy(), df_iss[df_iss['ItemCode'] == selected_item].copy()

past_rec, past_iss = i_rec[i_rec['ReceivedDate'] < start_dt], i_iss[i_iss['IssuedDate'] < start_dt]
curr_rec, curr_iss = i_rec[(i_rec['ReceivedDate'] >= start_dt) & (i_rec['ReceivedDate'] <= end_dt)], i_iss[(i_iss['IssuedDate'] >= start_dt) & (i_iss['IssuedDate'] <= end_dt)]


# =========================================================================
# --- GLOBAL MATH ENGINES (CALCULATE EVERYTHING BEFORE RENDERING TABS) ---
# =========================================================================

# 1. SOH Table Math
current_items_list = sorted(list(set(i_open['ItemCode'].unique()) | set(i_rec['ItemCode'].unique()) | set(i_iss['ItemCode'].unique())))
soh_table = pd.DataFrame({'ItemCode': current_items_list})
soh_table['ItemDescription'] = soh_table['ItemCode'].map(desc_mapping).fillna('Unknown')
adj_opening = i_open.groupby('ItemCode')['Balance'].sum().add(past_rec.groupby('ItemCode')['ReceivedQuantity'].sum(), fill_value=0).sub(past_iss.groupby('ItemCode')['IssuedQuantity'].sum(), fill_value=0).reset_index(name='Opening')
soh_table = soh_table.merge(adj_opening, on='ItemCode', how='left').merge(curr_rec.groupby('ItemCode')['ReceivedQuantity'].sum().reset_index(name='Total Received'), on='ItemCode', how='left').merge(curr_iss.groupby('ItemCode')['IssuedQuantity'].sum().reset_index(name='Total Issued'), on='ItemCode', how='left').fillna(0)
soh_table['Current Stock on Hand'] = soh_table['Opening'] + soh_table['Total Received'] - soh_table['Total Issued']
soh_table = pd.concat([soh_table, pd.DataFrame({'ItemCode': ['TOTAL'], 'ItemDescription': ['-'], 'Opening': [soh_table['Opening'].sum()], 'Total Received': [soh_table['Total Received'].sum()], 'Total Issued': [soh_table['Total Issued'].sum()], 'Current Stock on Hand': [soh_table['Current Stock on Hand'].sum()]})], ignore_index=True)

# 2. Timeline Math
start_month, end_month = pd.to_datetime(start_date).to_period('M'), pd.to_datetime(end_date).to_period('M')
if start_month == end_month: end_month = start_month + 2 
all_months = pd.period_range(start=start_month, end=end_month, freq='M')
item_month_records = []
for item in [i for i in current_items_list if i != 'TOTAL']:
    item_opening = adj_opening[adj_opening['ItemCode'] == item]['Opening'].sum()
    current_soh = float(item_opening) if not pd.isna(item_opening) else 0.0
    for m in all_months:
        current_soh += float(curr_rec[(curr_rec['ItemCode'] == item) & (curr_rec['ReceivedDate'].dt.to_period('M') == m)]['ReceivedQuantity'].sum() - curr_iss[(curr_iss['ItemCode'] == item) & (curr_iss['IssuedDate'].dt.to_period('M') == m)]['IssuedQuantity'].sum())
        item_month_records.append({'Item': f"{item} - {desc_mapping.get(item, 'Unknown')}", 'Month': str(m), 'SOH': current_soh})
timeline_df = pd.DataFrame(item_month_records) if item_month_records else pd.DataFrame()

# 3. Batch Summary & Risk Math
tx_open = pd.merge(pd.merge(i_open.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['Balance'].sum().reset_index(), past_rec.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['ReceivedQuantity'].sum().reset_index(), on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='outer').fillna(0), past_iss.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['IssuedQuantity'].sum().reset_index(), on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='outer').fillna(0)
tx_open['True_Opening'] = tx_open['Balance'] + tx_open['ReceivedQuantity'] - tx_open['IssuedQuantity']
batch_summary = tx_open.rename(columns={'True_Opening': 'Opening'})[['ItemCode', 'BatchNumber', 'ExpiryDate', 'Opening']].merge(curr_rec.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['ReceivedQuantity'].sum().reset_index(name='Received'), on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='outer').merge(curr_iss.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['IssuedQuantity'].sum().reset_index(name='Issued'), on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='outer').fillna(0)
batch_summary = batch_summary[(batch_summary['Opening'] != 0) | (batch_summary['Received'] != 0) | (batch_summary['Issued'] != 0)]
batch_summary['Current SOH'] = batch_summary['Opening'] + batch_summary['Received'] - batch_summary['Issued']
batch_summary = batch_summary.merge(i_iss[(i_iss['IssuedDate'] > (end_dt - pd.DateOffset(months=amc_window))) & (i_iss['IssuedDate'] <= end_dt)].groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['IssuedQuantity'].sum().reset_index(name='Rolling_Issued'), on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='left').fillna({'Rolling_Issued': 0})
batch_summary['AMC'] = batch_summary['Rolling_Issued'] / amc_window
batch_summary['MOS'] = np.where(batch_summary['AMC'] > 0, np.floor((batch_summary['Current SOH'] / batch_summary['AMC']) * 10) / 10, 999.0)
batch_summary['Remaining Shelf Life (Months)'] = np.floor((pd.to_datetime(batch_summary['ExpiryDate'], format='%Y-%m', errors='coerce') - pd.Timestamp.today()).dt.days / 365.25 * 12)

def assign_risk(r):
    rl, mos = r['Remaining Shelf Life (Months)'], r['MOS']
    if pd.isna(rl): return "Unknown Expiry"
    elif rl < min_stock: return f"🔴 High Expiry Risk (< {min_stock} Months)"
    elif mos >= 999.0: return "⚪ No Consumption (0 AMC)"
    elif mos > min_stock and rl < mos: return "🟠 Risk (Expires before consumed)"
    elif mos < min_stock: return f"🟡 Understocked (MOS < {min_stock})"
    elif mos > max_stock: return f"🔵 Overstocked (MOS > {max_stock})"
    return "🟢 Safe"
batch_summary['Risk Status'] = batch_summary.apply(assign_risk, axis=1)
batch_summary['Risk Quantity'] = batch_summary.apply(lambda r: max(0, round(r['Current SOH'] - (r['AMC'] * max(0, r['Remaining Shelf Life (Months)'])))) if "Risk" in str(r['Risk Status']) or "No Consumption" in str(r['Risk Status']) else 0, axis=1)
batch_summary['ItemDescription'] = batch_summary['ItemCode'].map(desc_mapping).fillna('Unknown')
batch_summary['Batch Label'] = batch_summary['ItemCode'] + " (Batch: " + batch_summary['BatchNumber'] + ")"

# 4. Lead Time Math
lead_time_df = pd.DataFrame()
if not curr_iss.empty and 'ReceivedbyFacility' in curr_iss.columns:
    lead_time_df = curr_iss.copy()
    lead_time_df['Delivery Days'] = (lead_time_df['ReceivedbyFacility'] - lead_time_df['IssuedDate']).dt.days
    lead_time_df = lead_time_df.dropna(subset=['Delivery Days'])


# =========================================================================
# --- RENDER TABS ---
# =========================================================================
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👁️ Overview", "📦 SOH Summary", "📈 SOH Trend", "📝 Transaction Ledger", 
    "⚠️ Expiry Risk", "🗓️ Monthly Matrices", "🚚 Lead Time"
])

# --- TAB 0: EXECUTIVE OVERVIEW (THE 2X2 DASHBOARD) ---
with tab0:
    st.write("") # Padding
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='text-align: center; color: #0F4C81;'>Current SOH by Item</h4>", unsafe_allow_html=True)
        df_soh_plot = soh_table[soh_table['ItemCode'] != 'TOTAL']
        if not df_soh_plot.empty:
            # ✨ NEW: Added hover_data for ItemDescription
            fig1 = px.bar(df_soh_plot, x='ItemCode', y='Current Stock on Hand', text='Current Stock on Hand', hover_data=['ItemDescription'])
            fig1.update_traces(textposition='outside', marker_color='#0F4C81')
            fig1.update_layout(xaxis_title="", yaxis_title="Quantity", height=350, margin=dict(t=20, b=0))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available.")

    with col2:
        st.markdown("<h4 style='text-align: center; color: #0F4C81;'>Expected Expiry Risk by Batch</h4>", unsafe_allow_html=True)
        risk_chart_df = batch_summary[batch_summary['Risk Quantity'] > 0]
        if not risk_chart_df.empty:
            color_map = { f"🔴 High Expiry Risk (< {min_stock} Months)": "#d62728", "🟠 Risk (Expires before consumed)": "#ff7f0e", "⚪ No Consumption (0 AMC)": "#6c757d" }
            # ✨ NEW: Added hover_data for ItemDescription
            fig2 = px.bar(risk_chart_df.sort_values('Risk Quantity', ascending=True), x='Risk Quantity', y='Batch Label', orientation='h', color='Risk Status', color_discrete_map=color_map, text='Risk Quantity', hover_data=['ItemDescription'])
            fig2.update_traces(textposition='outside')
            # ✨ NEW: Removed showlegend=False and positioned the legend neatly at the bottom
            fig2.update_layout(xaxis_title="Quantity at Risk", yaxis_title="", height=350, margin=dict(t=20, b=0), legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, title=""))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.success("No batches currently at risk.")

    st.write("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<h4 style='text-align: center; color: #0F4C81;'>Delivery Lead Time by Facility (Days)</h4>", unsafe_allow_html=True)
        if not lead_time_df.empty:
            # ✨ NEW: Mapped ItemDescription to lead_time_df so it can be hovered over
            lead_time_df['ItemDescription'] = lead_time_df['ItemCode'].map(desc_mapping).fillna('Unknown')
            # ✨ NEW: Removed points="all" to get rid of the horizontal dots and just show clean vertical boxes
            fig3 = px.box(lead_time_df, x='IssueToFacility', y='Delivery Days', hover_data=['ItemCode', 'ItemDescription'])
            fig3.update_traces(marker_color='#1E3A8A')
            fig3.update_layout(xaxis_title="", yaxis_title="Days", height=350, margin=dict(t=20, b=0))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No delivery data available.")

    with col4:
        st.markdown("<h4 style='text-align: center; color: #0F4C81;'>Latest MOS Distribution by Status</h4>", unsafe_allow_html=True)
        if not batch_summary.empty:
            plot_mos_df = batch_summary.copy()
            plot_mos_df['Visual MOS'] = np.where(plot_mos_df['MOS'] >= 999.0, max_stock + 12, plot_mos_df['MOS'])
            
            # ✨ NEW: Embedded the ItemDescription directly into the bold hover text for the Strip Plot
            plot_mos_df['Hover Text'] = plot_mos_df.apply(lambda r: f"{r['Batch Label']}<br>{r['ItemDescription']}<br>MOS: 999.0 (No Consumption)" if r['MOS'] >= 999.0 else f"{r['Batch Label']}<br>{r['ItemDescription']}<br>MOS: {r['MOS']}", axis=1)
            
            mos_color_map = { f"🔴 High Expiry Risk (< {min_stock} Months)": "#d62728", "🟠 Risk (Expires before consumed)": "#ff7f0e", "⚪ No Consumption (0 AMC)": "#6c757d", f"🟡 Understocked (MOS < {min_stock})": "#bcbd22", f"🔵 Overstocked (MOS > {max_stock})": "#1f77b4", "🟢 Safe": "#2ca02c", "Unknown Expiry": "#333333" }
            
            fig4 = px.strip(plot_mos_df, x='Visual MOS', y='Risk Status', color='Risk Status', hover_name='Hover Text', color_discrete_map=mos_color_map, stripmode='overlay')
            fig4.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='White')))
            fig4.update_layout(xaxis_title="Months of Stock (MOS)", yaxis_title="", showlegend=False, height=350, margin=dict(t=20, b=0))
            fig4.add_vrect(x0=min_stock, x1=max_stock, fillcolor="green", opacity=0.08, line_width=0, annotation_text="Safe Zone", annotation_position="top left")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No batch data available.")

# --- TAB 1: SOH SUMMARY ---
with tab1:
    st.dataframe(soh_table[['ItemCode', 'ItemDescription', 'Opening', 'Total Received', 'Total Issued', 'Current Stock on Hand']].style.format({
        'Opening': '{:,.0f}', 'Total Received': '{:,.0f}', 'Total Issued': '{:,.0f}', 'Current Stock on Hand': '{:,.0f}'
    }), use_container_width=True, hide_index=True)


# --- TAB 2: SOH TREND ---
with tab2:
    if not timeline_df.empty:
        fig_line = px.line(timeline_df, x='Month', y='SOH', color='Item', markers=True, title="Cumulative Stock on Hand by Item", labels={'Month': 'Year-Month', 'SOH': 'Stock on Hand'})
        fig_line.update_traces(line_width=3, marker_size=8)
        fig_line.update_layout(height=600, legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title="Item Legend"), margin=dict(r=150))
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available to plot trend.")


# --- TAB 3: TRANSACTION LEDGER ---
with tab3:
    ledger_rows = []
    for _, r in tx_open.iterrows():
        if r['True_Opening'] != 0: ledger_rows.append({'ItemCode': r['ItemCode'], 'BatchNumber': r['BatchNumber'], 'ExpiryDate': r['ExpiryDate'], 'Date_sort': pd.to_datetime(start_date) - pd.Timedelta(seconds=1), 'Date': pd.to_datetime(start_date).strftime('%d-%b-%y'), 'Month/Year': pd.to_datetime(start_date).strftime('%b-%y'), 'Reference / Facility': 'Opening Balance', 'Opening': r['True_Opening'], 'Received': 0, 'Issued': 0})
    for _, r in curr_rec.iterrows():
        if r['ReceivedQuantity'] > 0: ledger_rows.append({'ItemCode': r['ItemCode'], 'BatchNumber': r['BatchNumber'], 'ExpiryDate': r['ExpiryDate'], 'Date_sort': pd.to_datetime(r['ReceivedDate']), 'Date': pd.to_datetime(r['ReceivedDate']).strftime('%d-%b-%y'), 'Month/Year': pd.to_datetime(r['ReceivedDate']).strftime('%b-%y'), 'Reference / Facility': str(r.get('WayBill', r.get('Donor', 'Received'))) if str(r.get('WayBill', r.get('Donor', 'Received'))).strip() not in ['nan', ''] else 'Received', 'Opening': 0, 'Received': r['ReceivedQuantity'], 'Issued': 0})
    for _, r in curr_iss.iterrows():
        if r['IssuedQuantity'] > 0: ledger_rows.append({'ItemCode': r['ItemCode'], 'BatchNumber': r['BatchNumber'], 'ExpiryDate': r['ExpiryDate'], 'Date_sort': pd.to_datetime(r['IssuedDate']), 'Date': pd.to_datetime(r['IssuedDate']).strftime('%d-%b-%y'), 'Month/Year': pd.to_datetime(r['IssuedDate']).strftime('%b-%y'), 'Reference / Facility': str(r.get('IssueToFacility', 'Issued')) if str(r.get('IssueToFacility', 'Issued')).strip() not in ['nan', ''] else 'Issued', 'Opening': 0, 'Received': 0, 'Issued': r['IssuedQuantity']})

    if ledger_rows:
        ledger_df = pd.DataFrame(ledger_rows).sort_values(['ItemCode', 'BatchNumber', 'ExpiryDate', 'Date_sort'])
        ledger_df['ExpiryDate_Display'] = pd.to_datetime(ledger_df['ExpiryDate'], format='%Y-%m', errors='coerce').dt.strftime('%b-%y').fillna(ledger_df['ExpiryDate'])
        ledger_df['Net'] = ledger_df['Opening'] + ledger_df['Received'] - ledger_df['Issued']
        ledger_df['Balance'] = ledger_df.groupby(['ItemCode', 'BatchNumber', 'ExpiryDate'])['Net'].cumsum()
        ledger_df['ItemDescription'] = ledger_df['ItemCode'].map(desc_mapping).fillna('Unknown')
        ledger_df = ledger_df.merge(batch_summary[['ItemCode', 'BatchNumber', 'ExpiryDate', 'Risk Status', 'Remaining Shelf Life (Months)', 'Current SOH', 'AMC', 'MOS', 'Risk Quantity']], on=['ItemCode', 'BatchNumber', 'ExpiryDate'], how='left')
        
        st.markdown("""<div style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; font-family: sans-serif;"><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #ffcccc; border: 1px solid #900000; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>High Expiry Risk</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #ffe8cc; border: 1px solid #cc5c00; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Risk (Expires before consumed)</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #e2e3e5; border: 1px solid #6c757d; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>No Consumption</strong> (0 AMC)</span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #fff4cc; border: 1px solid #8a6d00; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Understocked</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #cce5ff; border: 1px solid #004085; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Overstocked</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #ccffcc; border: 1px solid #006600; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Safe (Stocked to Plan)</strong></span></div></div>""", unsafe_allow_html=True)
        
        display_ledger = ledger_df[['Date', 'Month/Year', 'Reference / Facility', 'ItemCode', 'ItemDescription', 'BatchNumber', 'ExpiryDate_Display', 'Opening', 'Received', 'Issued', 'Balance', 'Remaining Shelf Life (Months)', 'Current SOH', 'AMC', 'MOS', 'Risk Quantity', 'Risk Status']].rename(columns={'ExpiryDate_Display': 'ExpiryDate', 'Remaining Shelf Life (Months)': 'Remaining Shelf-life', 'AMC': 'Adjacent AMC', 'MOS': 'Current MOS', 'Risk Quantity': 'Expiry Risk Qty'}).copy()
        
        def highlight_row(r):
            s = str(r.get('Risk Status', ''))
            if '🔴' in s: return ['background-color: #ffcccc; color: #900000;'] * len(r)
            elif '🟠' in s: return ['background-color: #ffe8cc; color: #cc5c00;'] * len(r)
            elif '⚪' in s: return ['background-color: #e2e3e5; color: #383d41;'] * len(r)
            elif '🟡' in s: return ['background-color: #fff4cc; color: #8a6d00;'] * len(r)
            elif '🔵' in s: return ['background-color: #cce5ff; color: #004085;'] * len(r)
            elif '🟢' in s: return ['background-color: #ccffcc; color: #006600;'] * len(r)
            return [''] * len(r)

        st.dataframe(display_ledger.style.apply(highlight_row, axis=1).format({'Opening': lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x > 0 else "-", 'Received': lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x > 0 else "-", 'Issued': lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x > 0 else "-", 'Balance': '{:,.0f}', 'Remaining Shelf-life': '{:,.0f}', 'Current SOH': '{:,.0f}', 'Adjacent AMC': '{:,.1f}', 'Current MOS': '{:,.1f}', 'Expiry Risk Qty': '{:,.0f}'}), use_container_width=True, hide_index=True)
    else:
        st.info("No transaction history found.")


# --- TAB 4: EXPIRY RISK ---
with tab4:
    if not risk_chart_df.empty:
        fig_risk = px.bar(risk_chart_df.sort_values('Risk Quantity', ascending=True), x='Risk Quantity', y='Batch Label', orientation='h', color='Risk Status', color_discrete_map=color_map, text='Risk Quantity')
        fig_risk.update_traces(textposition='outside')
        fig_risk.update_layout(xaxis_title="Guaranteed Quantity to Expire", yaxis_title="", height=600)
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.success("🎉 No batches currently have a mathematically projected expiry risk.")


# --- TAB 5: MATRICES ---
with tab5:
    if not batch_summary.empty:
        lookback_start = start_month - amc_window 
        full_date_range = pd.period_range(start=lookback_start, end=end_month, freq='M')
        soh_records, amc_records, mos_records = [], [], []
        
        for _, row in batch_summary.iterrows():
            item, desc, batch, exp = row['ItemCode'], row['ItemDescription'], row['BatchNumber'], row['ExpiryDate']
            current_soh = row['Opening']
            soh_data, amc_data, mos_data = {'ItemCode': item, 'BatchNumber': batch, 'ExpiryDate': exp}, {'ItemCode': item, 'BatchNumber': batch, 'ExpiryDate': exp}, {'ItemCode': item, 'BatchNumber': batch, 'ExpiryDate': exp}
            
            batch_curr_rec, batch_curr_iss = curr_rec[(curr_rec['ItemCode'] == item) & (curr_rec['BatchNumber'] == batch) & (curr_rec['ExpiryDate'] == exp)], curr_iss[(curr_iss['ItemCode'] == item) & (curr_iss['BatchNumber'] == batch) & (curr_iss['ExpiryDate'] == exp)]
            monthly_iss = i_iss[(i_iss['ItemCode'] == item) & (i_iss['BatchNumber'] == batch) & (i_iss['ExpiryDate'] == exp)].copy()
            monthly_iss['Month'] = monthly_iss['IssuedDate'].dt.to_period('M')
            rolling_amc_series = monthly_iss.groupby('Month')['IssuedQuantity'].sum().reindex(full_date_range, fill_value=0).rolling(window=amc_window, min_periods=1).sum() / amc_window
            
            for m in all_months:
                current_soh += batch_curr_rec[batch_curr_rec['ReceivedDate'].dt.to_period('M') == m]['ReceivedQuantity'].sum() - batch_curr_iss[batch_curr_iss['IssuedDate'].dt.to_period('M') == m]['IssuedQuantity'].sum()
                adjacent_amc = rolling_amc_series[m]
                m_str = m.strftime('%b %Y')
                soh_data[m_str], amc_data[m_str], mos_data[m_str] = current_soh, adjacent_amc, np.floor((current_soh / adjacent_amc) * 10) / 10 if adjacent_amc > 0 else (999.0 if current_soh > 0 else 0.0)
            
            soh_records.append(soh_data); amc_records.append(amc_data); mos_records.append(mos_data)
            
        st.subheader("📦 Monthly SOH Matrix"); st.dataframe(pd.DataFrame(soh_records).style.format(precision=0), use_container_width=True, hide_index=True)
        st.subheader("📊 Monthly AMC Matrix"); st.dataframe(pd.DataFrame(amc_records).style.format(precision=1), use_container_width=True, hide_index=True)
        st.subheader("🗓️ Monthly MOS Matrix")
        st.markdown("""<div style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; font-family: sans-serif;"><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #ffcccc; border: 1px solid #900000; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Stock Out</strong> (0)</span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #fff4cc; border: 1px solid #8a6d00; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Below Min</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #ccffcc; border: 1px solid #006600; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Stocked to Plan</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #cce5ff; border: 1px solid #004085; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>Above Max</strong></span></div><div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #e2e3e5; border: 1px solid #6c757d; border-radius: 3px;"></div><span style="font-size: 0.9em; color: #333;"><strong>No Consumption</strong> (0 AMC)</span></div></div>""", unsafe_allow_html=True)
        
        def color_mos(v):
            try: v = float(v)
            except: return '' 
            if v == 0: return 'background-color: #ffcccc; color: #900000;' 
            elif v >= 999.0: return 'background-color: #e2e3e5; color: #383d41;' 
            elif 0 < v < min_stock: return 'background-color: #fff4cc; color: #8a6d00;' 
            elif min_stock <= v <= max_stock: return 'background-color: #ccffcc; color: #006600;' 
            elif v > max_stock: return 'background-color: #cce5ff; color: #004085;' 
            return ''
        st.dataframe(pd.DataFrame(mos_records).style.format(precision=1).map(color_mos, subset=[m.strftime('%b %Y') for m in all_months]), use_container_width=True, hide_index=True)


# --- TAB 6: LEAD TIME ---
with tab6:
    if not lead_time_df.empty:
        lt_summary = lead_time_df.groupby('IssueToFacility').agg({'Delivery Days': ['mean', 'min', 'max', 'count']}).reset_index()
        lt_summary.columns = ['Facility', 'Avg Lead Time (Days)', 'Fastest Delivery (Days)', 'Slowest Delivery (Days)', 'Total Shipments']
        st.dataframe(lt_summary.style.format({'Avg Lead Time (Days)': '{:.1f}', 'Fastest Delivery (Days)': '{:.0f}', 'Slowest Delivery (Days)': '{:.0f}'}), use_container_width=True, hide_index=True)
    else:
        st.info("No delivery lead time data available.")