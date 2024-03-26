import streamlit as st
import random
import serial
import time

# Function to shuffle node data
def shuffle_node_data(node_data):
    random.shuffle(node_data)
    return node_data

# Initialize or reuse the serial connection
def init_serial_connection():
    # Check if 'ser' is in st.session_state and is not None, then check if it's open
    if 'ser' in st.session_state and st.session_state.ser is not None and st.session_state.ser.is_open:
        return  # Serial is already open, no action needed
    else:
        try:
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-210', 9600)
        except serial.SerialException as e:
            st.error(f"Failed to open serial port: {e}")
            st.session_state.ser = None  # Ensure 'ser' is set to None if opening fails
    
    # initialize timeout
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = 10
            
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
