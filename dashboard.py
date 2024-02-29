import streamlit as st
import random
import json
import serial

# Function to shuffle node data
def shuffle_node_data(node_data):
    random.shuffle(node_data)
    return node_data

# Initialize or reuse the serial connection
def init_serial_connection():
    if 'ser' not in st.session_state or not st.session_state.ser.is_open:
        try:
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-140', 9600)
        except serial.SerialException:
            st.error("Failed to open serial port. Check the connection and try again.")
            st.session_state.ser = None

# Streamlit UI setup
st.sidebar.image("logo.png", width=270)
st.header("🕒 Feed Time Scheduler ")
st.markdown("---")

# Settings Section with Emoji
st.subheader("⚙️ Settings")
feed_time = st.text_input("Enter feed time (HH : MM):", "13:00")
num_nodes = st.selectbox("Select the number of nodes:", range(4, 8))
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

# Create node data
node_data = list(range(1, num_nodes + 1))
ball_node_choice = None

if node_order_choice == 'Random':
    shuffle_node_data(node_data)
    ball_node_choice = random.choice(node_data)
else:
    custom_order = st.text_input("Enter the custom node order (comma-separated):", ','.join(map(str, node_data)))
    try:
        node_data = [int(i.strip()) for i in custom_order.split(',')]
        if len(node_data) != num_nodes or not all(1 <= n <= num_nodes for n in node_data):
            st.error("Please enter a valid node order.")
            node_data = list(range(1, num_nodes + 1))
    except ValueError:
        st.error("Please enter a valid node order.")
        node_data = list(range(1, num_nodes + 1))
    ball_node_choice = st.selectbox("Select the ball node:", node_data)

if st.button('Randomize Node Order and Ball Node'):
    shuffle_node_data(node_data)
    ball_node_choice = random.choice(node_data)

st.markdown("---")
st.subheader("📊 Selections")
st.write("Your feed time is ", feed_time)
st.write("Node order: ", ', '.join(map(str, node_data)))
if ball_node_choice is not None:
    st.write("Chosen ball node is ", ball_node_choice)

# Submit button to send data over serial port
if st.button('Submit and Send Data'):
    init_serial_connection()  # Ensure the serial connection is initialized
    if st.session_state.ser:
        data_to_send = {
            "feed_time": feed_time,
            "node_order": node_data,
            "ball_node": ball_node_choice
        }
        json_data = json.dumps(data_to_send)
        try:
            # Sending the trigger command for RF transmission
            st.session_state.ser.write("SEND_RF\n".encode())
            st.success("Data sent over serial port")
        except Exception as e:
            st.error(f"Failed to send data: {e}")
