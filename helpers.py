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
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-1140', 9600)
            # Optionally, you can add a success message or log here
        except serial.SerialException as e:
            st.error(f"Failed to open serial port: {e}")
            st.session_state.ser = None  # Ensure 'ser' is set to None if opening fails
            
def send_activation_command(feeder_id):
    command_code = 100  # Activation
    activation_command = str(command_code) + str(feeder_id)
    if st.session_state.ser:
        try:
            st.session_state.ser.write(activation_command.encode())
            st.success(f"Activation command sent to feeder {feeder_id}")
        except Exception as e:
            st.error(f"Failed to send activation command to feeder {feeder_id}: {e}")

def wait_for_feedback(feeder_id):
    feedback_code = 2000  # Finished
    expected_feedback = str(feedback_code + feeder_id)
    feedback_received = False
    start_time = time.time()
    timeout_seconds = 10  # Set a timeout for feedback

    while not feedback_received and (time.time() - start_time) < timeout_seconds:
        if st.session_state.ser.in_waiting > 0:
            incoming_data = st.session_state.ser.readline().decode().strip()
            print(f"Received: {incoming_data}, Expected: {expected_feedback}")
            if incoming_data == expected_feedback:
                st.success(f"Feedback received from feeder {feeder_id}")
                feedback_received = True
            else:
                # Handle unexpected feedback echoing??????
                # st.error(f"Unexpected feedback received: {incoming_data}")
                x=1
        time.sleep(0.1)  # Avoid busy waiting
    
    if not feedback_received:
        st.error(f"Timeout waiting for feedback from feeder {feeder_id}")