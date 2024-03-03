import streamlit as st
import random
import json
import serial
import time
from datetime import datetime

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

# Send data, schedule retry if needed
def attempt_send_data(data_to_send, force_retry=False):
  if not st.session_state.ser:
    st.error("Serial port is not open.")
    return

  if force_retry or 'last_attempt_time' not in st.session_state:
    retry_interval = random.randint(30*60, 60*60)  # Random retry interval in seconds
    current_time = time.time()
    last_attempt_time = st.session_state.get('last_attempt_time', 0)
      
    if force_retry or current_time - last_attempt_time > retry_interval:
      try:
        st.session_state.ser.write(json.dumps(data_to_send).encode())
        st.session_state.last_attempt_time = current_time
        st.success("Data sent over serial port. Awaiting response...")
      except Exception as e:
        st.error(f"Failed to send data: {e}")
    else:
      st.info("Waiting for the next retry interval before sending data again.")
  else:
      st.info("Data send attempt already in progress. Please wait.")

# Initialize scheduled_feedings if not in session state
def init_scheduled_feedings():
  if '__scheduled_feedings' not in st.session_state:
    st.session_state.__scheduled_feedings = {}

# Schedule new feeding time, check for duplicates
def schedule_new_feeding(new_feed_time, data_to_send):
  new_feed_time_obj = datetime.strptime(new_feed_time, "%H:%M")
  formatted_time = new_feed_time_obj.strftime("%I:%M %p")
    
  if formatted_time in st.session_state.__scheduled_feedings:
    st.error(f"A feeding is already scheduled for {formatted_time}. Please choose a different time.")
  else:
    st.session_state.__scheduled_feedings[formatted_time] = data_to_send
    st.success(f"New feeding scheduled for {formatted_time}.")

# UI setup
st.sidebar.image("logo.png", width=270)
st.header("🕒 Feed Time Scheduler")
st.markdown("---")

# Settings
st.subheader("⚙️ Settings")
num_nodes = st.selectbox("Select the number of nodes:", range(4, 8))
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

# Create node data
node_data = list(range(1, num_nodes + 1))
ball_node_choice = None

# Node order selection logic
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

# Schedule feeding
st.markdown("---")
st.subheader("📅 Schedule Multiple Feedings")
init_scheduled_feedings()
new_feed_time = st.text_input("Enter new feed time (HH : MM):", "13:00")

# Submit button to schedule a new feeding
if st.button('Schedule New Feeding'):
  data_to_send = {
    "feed_time": new_feed_time,
    "node_order": node_data,
    "ball_node": ball_node_choice
  }
  try:
    schedule_new_feeding(new_feed_time, data_to_send)
  except ValueError:
    st.error("Please enter a valid time in HH:MM format.")

# Display scheduled feedings
st.markdown("---")
st.subheader("📅 Scheduled Feedings")
if st.session_state.__scheduled_feedings:
  for feed_time, data in st.session_state.__scheduled_feedings.items():
    st.write(f"Feeding time: {feed_time}; Data: {json.dumps(data)}")
else:
  st.info("No scheduled feedings yet.")
