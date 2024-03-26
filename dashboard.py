import streamlit as st
import datetime
import random
from helpers import *
import pandas as pd
import numpy as np
import plotly.express as px

# Initialize feed_time in session_state if it doesn't exist
if 'feed_time' not in st.session_state:
    st.session_state.feed_time = datetime.datetime.now().time()

# UI setup
st.sidebar.image("logo.png", width=270)
st.header("🕒 Feed Time Scheduler")

# Display current feed status
if 'feed_status' not in st.session_state:
    st.session_state.feed_status = "Not scheduled"

# System Status in the sidebar
st.sidebar.subheader("📊 System Status")
st.sidebar.write(f"Feed Status: {st.session_state.feed_status}")

# Settings UI components
with st.expander("⚙️ Advanced Settings"):
    st.subheader("Welcome to settings!")
    st.caption("Here you can adjust the timeout for feedback and other parameters.")
    
    # Set custom timeout
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = "10"
    timeout_seconds = st.text_input("Set custom timeout for feedback (in seconds):", st.session_state.timeout_seconds)
    if st.button('Save Settings'):
        st.session_state.timeout_seconds = timeout_seconds
        st.success("Settings saved!")

# Use session_state for feed_time to persist its value
feed_time = st.time_input("Select feed time:", st.session_state.feed_time)

# Update session_state with the new feed_time after user interaction
st.session_state.feed_time = feed_time

# Number of nodes with a slider
num_nodes = st.slider("Select the number of nodes:", min_value=2, max_value=7, value=3)

# Node order configuration
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

# Node data configuration
node_data = list(range(1, num_nodes + 1))
if node_order_choice == 'Random':
    node_data = shuffle_node_data(node_data)
    ball_node_choice = random.choice(node_data)
else:
    custom_order = st.text_input("Enter the custom node order (comma-separated):", ','.join(map(str, node_data)))
    try:
        node_data = [int(i.strip()) for i in custom_order.split(',')]
        if len(node_data) != num_nodes or not all(1 <= n <= num_nodes for n in node_data):
            st.error("Please enter a valid node order.")
            node_data = list(range(1, num_nodes + 1))
        else:
            ball_node_choice = st.selectbox("Select the ball node:", node_data)
    except ValueError:
        st.error("Please enter numbers only in the node order.")
        node_data = list(range(1, num_nodes + 1))

# Submit and schedule feeding
if st.button('Submit and Send Data'):
    init_serial_connection()
    # Example of checking for a simulated serial connection state for demonstration
    if 'ser' not in st.session_state:
        st.session_state['ser'] = True  # Simulate serial connection being established
    if st.session_state['ser']:
        # Placeholder for sending data and recording activation times
        feed_time_str = st.session_state.feed_time.strftime('%H:%M')  # Use stored feed time
        st.session_state['feed_status'] = f"Scheduled for {feed_time_str}"
        st.sidebar.success("Feed time scheduled.")
    else:
        st.sidebar.error("Serial connection not initialized. Cannot send data.")

# System Status and selections moved to sidebar
feed_time_str = st.session_state.feed_time.strftime('%H:%M')
node_order = ', '.join(map(str, node_data))
st.sidebar.write("Feed time selected is:", feed_time_str)
st.sidebar.write("Node order:", node_order)
if 'ball_node_choice' in locals():
    st.sidebar.write("Chosen ball node is:", ball_node_choice)
st.sidebar.write("The timeout for each node (in seconds) is:", st.session_state.get('timeout_seconds', 'Not set'))

# Node Activation Stats Section
st.markdown("---")
st.subheader("📈 Node Activation Stats")

activation_times = np.random.randint(1, 15, size=len(node_data))
df = pd.DataFrame({
    'Node': ['Node ' + str(node) for node in node_data],  # Use the user-defined order
    'Activation Time (s)': activation_times
})

# DataFrame styling for a nicer look
st.dataframe(df.style.format(precision=2)
             .highlight_max(subset=['Activation Time (s)'], color='lightgreen')
             .set_properties(**{'text-align': 'center'}), height=300)

# Plotting with Plotly for an interactive chart
fig = px.bar(df, x='Node', y='Activation Time (s)', text='Activation Time (s)',
             color='Activation Time (s)', labels={'Activation Time (s)': 'Activation Time (seconds)'},
             category_orders={"Node": [f"Node {n}" for n in node_data]})  # Use the user-defined order for categories

fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': [f"Node {n}" for n in node_data]}, 
                  yaxis=dict(title='Seconds'), title='Node Activation Times')
fig.update_traces(texttemplate='%{text}s', textposition='outside')
st.plotly_chart(fig, use_container_width=True)
