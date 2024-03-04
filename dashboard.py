import streamlit as st
import random
from helpers import *

# Settings Section with Emoji
st.subheader("⚙️ Settings")
feed_time = st.text_input("Enter feed time (HH : MM):", "13:00")
num_nodes = st.selectbox("Select the number of nodes:", range(2, 8))
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

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

# Display selected settings
st.markdown("---")
st.subheader("📊 Selections")
st.write("Your feed time is:", feed_time)
st.write("Node order:", ', '.join(map(str, node_data)))
if ball_node_choice is not None:
    st.write("Chosen ball node is:", ball_node_choice)

# Submit button to send data over serial port and activate feeders sequentially
if st.button('Submit and Send Data'):
    init_serial_connection()
    if st.session_state.ser:
        for feeder_id in node_data:
            send_activation_command(feeder_id)
            wait_for_feedback(feeder_id)
        st.success("All feeders activated and feedback received.")
    else:
        st.error("Serial connection not initialized. Cannot send data.")