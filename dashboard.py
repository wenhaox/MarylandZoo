import streamlit as st
import random
from helpers import *

# Check if settings page is shown or not
# if 'show_settings' not in st.session_state:
#     st.session_state.show_settings = False

# UI setup
st.sidebar.image("logo.png", width=270)
st.header("🕒 Feed Time Scheduler")
st.markdown("---")

# Button to toggle settings (keep button in top right)
with st.expander("⚙️ Settings"):
    st.subheader("Welcome to settings!")
    st.caption("Here you can adjust the timeout for feedback and other parameters.")
    
    # set custom timeout
    st.write("Set custom timeout for feedback (in seconds)")
    timeout_seconds = st.text_input("Enter timeout in seconds:", "10")
    st.divider()

    # section 2
    st.write("")

    # save settings
    if (st.button('Save', type="primary")):
        st.session_state.timeout_seconds = timeout_seconds
        st.success("Timeout saved!")

# Determine Node Order
st.subheader("⚙️ Determine Node Order")
feed_time = st.text_input("Enter feed time (HH : MM):", "13:00")
num_nodes = st.selectbox("Select the number of nodes:", range(2, 8))
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

# adjust timeout seconds
# timeout_seconds = st.slider("Set timeout (in seconds) for feedback:", 1, 60, 10, 1)

# Create node data
node_data = list(range(1, num_nodes + 1))
ball_node_choice = None

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

# Submit button to send data over serial port and activate feeders sequentially
if st.button('Submit and Send Data'):
    init_serial_connection()
    if st.session_state.ser:
        for feeder_id in node_data:
            is_ball_node = (feeder_id == ball_node_choice)
            send_activation_command(feeder_id, is_ball_node)
            wait_for_feedback(feeder_id, is_ball_node)
        st.sidebar.success("All feeders activated and feedback received.")
    else:
        st.sidebar.error("Serial connection not initialized. Cannot send data.")

# Display selected parameters
st.markdown("---")
st.subheader("📊 Selections")
st.write("Your feed time is:", feed_time)
st.write("Node order:", ', '.join(map(str, node_data)))
if ball_node_choice is not None:
    st.write("Chosen ball node is:", ball_node_choice)
st.write("The timeout for each node (in seconds) is:", timeout_seconds)

