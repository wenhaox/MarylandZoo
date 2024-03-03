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

# Send data for first time, schedule retry if needed
def attempt_send_data(data_to_send, force_retry=False):
  if not st.session_state.ser:
      st.error("Serial port is not open.")
      return

  # Check if it's first attempt or retry is needed
  if force_retry or 'last_attempt_time' not in st.session_state:
    retry_interval = random.randint(30*60, 60*60)  # Random retry interval in seconds
    current_time = time.time()
    last_attempt_time = st.session_state.get('last_attempt_time', 0)
    
    # Retry if boolean is true or the retry interval has passed
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

# Check and send data to schedule multiple feeding instances

# UI setup
st.sidebar.image("logo.png", width=270)
st.header("🕒 Feed Time Scheduler ")
st.markdown("---")

# Settings
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
    # try:
    #   # Sending the trigger command for RF transmission
    #   st.session_state.ser.write("SEND_RF\n".encode())
    #   st.success("Data sent over serial port")
    # except Exception as e:
    #   st.error(f"Failed to send data: {e}")
    attempt_send_data(data_to_send, force_retry=True) # send data a second time if first time fails

from datetime import datetime
import streamlit as st

# Function to initialize scheduled_feedings in session state if not present
def init_scheduled_feedings():
    if '__scheduled_feedings' not in st.session_state:
        st.session_state.__scheduled_feedings = {}

# Function to schedule a new feeding
def schedule_new_feeding(new_feed_time, data_to_send):
  # Time conversion
  new_feed_time_obj = datetime.strptime(new_feed_time, "%H:%M")
  formatted_time = new_feed_time_obj.strftime("%I:%M %p")
  
  # If feeding time exists, don't schedule it again
  if formatted_time in st.session_state.__scheduled_feedings:
    st.error(f"A feeding is already scheduled for {formatted_time}. Please choose a different time.")
  
  # Update session state with new feeding time and associated data
  else:
    st.session_state.__scheduled_feedings[formatted_time] = data_to_send
    st.success(f"New feeding scheduled for {formatted_time}.")

# UI setup for scheduling feedings
st.markdown("---")
st.subheader("📅 Schedule Multiple Feedings")
init_scheduled_feedings()
new_feed_time = st.text_input("Enter new feed time (HH : MM):", "13:00")
data_to_send = "Example data"  # This would be replaced with your actual data to send

if st.button("Schedule New Feeding"):
    try:
        schedule_new_feeding(new_feed_time, data_to_send)
    except ValueError:
        st.error("Please enter a valid time in HH:MM format.")

# UI setup for displaying scheduled feedings
st.markdown("---")
st.subheader("📅 Scheduled Feedings")
if st.session_state.__scheduled_feedings:
    for feed_time, data in st.session_state.__scheduled_feedings.items():
        st.write(f"Feeding time: {feed_time} - Data: {data}")
else:
    st.info("No scheduled feedings yet.")