import streamlit as st
import datetime
import random
from helpers import *
import pandas as pd
import numpy as np
import plotly.express as px

# Function to shuffle node data
def shuffle_node_data(node_data):
    random.shuffle(node_data)
    return node_data

def init_serial_connection():
    # Attempt to establish a serial connection if not already established or if it failed previously
    if 'ser' not in st.session_state or not isinstance(st.session_state.ser, serial.Serial) or not st.session_state.ser.is_open:
        try:
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-210', 9600)
            st.info("Serial connection established.")
        except serial.SerialException as e:
            st.error(f"Failed to open serial port: {e}")
            st.session_state.ser = False  # Indicate failure to establish connection
            
def send_activation_command(feeder_id, is_ball_node):
    command_code = 101 if is_ball_node else 100
    activation_command = str(command_code) + str(feeder_id)
    if st.session_state.ser:
        try:
            st.session_state.ser.write(activation_command.encode())
            st.sidebar.success(f"Activation command sent to feeder {feeder_id}")
        except Exception as e:
            st.sidebar.error(f"Failed to send activation command to feeder {feeder_id}: {e}")

def wait_for_feedback(feeder_id, is_ball_node):
    feedback_code = 2000
    expected_feedback = str(feedback_code + feeder_id)
    feedback_received = False
    start_time = time.time()
    # Ensure timeout_seconds is treated as an integer or float
    timeout_seconds = int(st.session_state.timeout_seconds)  # or use float() if you expect decimal values
    
    while not feedback_received and (time.time() - start_time) < timeout_seconds:
        if st.session_state.ser.in_waiting > 0:
            incoming_data = st.session_state.ser.readline().decode().strip()
            print(f"Received: {incoming_data}, Expected: {expected_feedback}")
            if incoming_data == expected_feedback:
                st.sidebar.success(f"Feedback received from feeder {feeder_id}")
                feedback_received = True
            else:
                # Handle unexpected feedback if necessary
                # st.error(f"Unexpected feedback received: {incoming_data}")
                pass  # Adjust as needed
        time.sleep(0.1)  # Avoid busy waiting
    
    if not feedback_received:
        st.sidebar.error(f"Timeout waiting for feedback from feeder {feeder_id}")
        
def initialize_session_states():
    if 'feed_time' not in st.session_state:
        st.session_state.feed_time = datetime.datetime.now().time()
    if 'feed_status' not in st.session_state:
        st.session_state.feed_status = "Not scheduled"
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = "10"

def setup_ui():
    st.sidebar.image("logo.png", width=270)
    st.header("🕒 Feed Time Scheduler")
    st.sidebar.subheader("📊 System Status")
    # Updating feed status display with nuanced feedback
    feed_status = st.session_state.feed_status
    if feed_status == "Not scheduled":
        st.sidebar.info("Feed Status: Not scheduled")
    elif feed_status == "Scheduled":
        st.sidebar.success("Feed Status: Scheduled")
    elif feed_status == "In Progress":
        st.sidebar.warning("Feed Status: Feeding now...")
    elif feed_status == "Failed":
        st.sidebar.error("Feed Status: Failed")
    elif feed_status == "Completed":
        st.sidebar.success("Feed Status: Completed successfully")


def configure_advanced_settings():
    with st.expander("⚙️ Advanced Settings"):
        st.subheader("Welcome to settings!")
        st.caption("Here you can adjust the timeout for feedback and other parameters.")
        timeout_seconds = st.text_input("Set custom timeout for feedback (in seconds):", st.session_state.timeout_seconds)
        if st.button('Save Settings'):
            st.session_state.timeout_seconds = int(timeout_seconds)  # Use float(timeout_seconds) if decimals are needed
            st.success("Settings saved!")

def feed_time_and_node_configuration():
    feed_time = st.time_input("Select feed time:", st.session_state.feed_time)
    st.session_state.feed_time = feed_time
    num_nodes = st.slider("Select the number of nodes:", min_value=2, max_value=4, value=2)
    node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))
    return num_nodes, node_order_choice

def configure_node_data(num_nodes, node_order_choice):
    node_data = list(range(1, num_nodes + 1))
    if node_order_choice == 'Random':
        node_data = shuffle_node_data(node_data)
        ball_node_choice = random.choice(node_data)
    else:
        custom_order = st.text_input("Enter the custom node order (comma-separated):", ','.join(map(str, node_data)))
        node_data, ball_node_choice = process_custom_order(custom_order, num_nodes)
    return node_data, locals().get('ball_node_choice')

def process_custom_order(custom_order, num_nodes):
    try:
        node_data = [int(i.strip()) for i in custom_order.split(',')]
        if len(node_data) != num_nodes or not all(1 <= n <= num_nodes for n in node_data):
            st.error("Please enter a valid node order.")
            return list(range(1, num_nodes + 1)), None
        else:
            return node_data, st.selectbox("Select the ball node:", node_data)
    except ValueError:
        st.error("Please enter numbers only in the node order.")
        return list(range(1, num_nodes + 1)), None

def submit_and_schedule_feeding(node_data, ball_node_choice):
    display_info(node_data, ball_node_choice)
    if st.button('Submit and Send Data'):
        init_serial_connection()
        # Only proceed if st.session_state.ser is a Serial object and the port is open
        if isinstance(st.session_state.ser, serial.Serial) and st.session_state.ser.is_open:
            try:
                for feeder_id in node_data:
                    is_ball_node = (feeder_id == ball_node_choice)
                    send_activation_command(feeder_id, is_ball_node)
                    wait_for_feedback(feeder_id, is_ball_node)
                st.sidebar.success("All feeders activated and feedback received.")
            except Exception as e:
                st.sidebar.error(f"Failed to activate feeders: {e}")
        else:
            st.sidebar.error("Serial connection not initialized. Cannot send data.")


def display_info(node_data, ball_node_choice):
    feed_time_str = st.session_state.feed_time.strftime('%H:%M')
    node_order = ', '.join(map(str, node_data))
    st.write("Feed time selected is:", feed_time_str)
    st.write("Node order:", node_order)
    if ball_node_choice:
        st.write("Chosen ball node is:", ball_node_choice)
    st.write("The timeout for each node (in seconds) is:", st.session_state.timeout_seconds)

def display_node_activation_stats(node_data):
    st.markdown("---")
    st.subheader("📈 Node Activation Stats")
    activation_times = np.random.randint(1, 15, size=len(node_data))
    df = pd.DataFrame({
        'Node': ['Node ' + str(node) for node in node_data],
        'Activation Time (s)': activation_times
    })

    # DataFrame styling for a nicer look
    styled_df = df.style.format(precision=2) \
        .highlight_max(subset=['Activation Time (s)'], color='lightgreen') \
        .set_properties(**{'text-align': 'center'})
    st.dataframe(styled_df, height=300)

    # Plotting with Plotly for an interactive chart
    fig = px.bar(df, x='Node', y='Activation Time (s)', text='Activation Time (s)',
                 color='Activation Time (s)', labels={'Activation Time (s)': 'Activation Time (seconds)'},
                 category_orders={"Node": [f"Node {n}" for n in node_data]})  # Use the user-defined order for categories

    fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': [f"Node {n}" for n in node_data]}, 
                      yaxis=dict(title='Seconds'), title='Node Activation Times')
    fig.update_traces(texttemplate='%{text}s', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

initialize_session_states()
setup_ui()
configure_advanced_settings()
num_nodes, node_order_choice = feed_time_and_node_configuration()
node_data, ball_node_choice = configure_node_data(num_nodes, node_order_choice)
submit_and_schedule_feeding(node_data, ball_node_choice)
display_node_activation_stats(node_data)