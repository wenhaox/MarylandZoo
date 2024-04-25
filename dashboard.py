import serial
import streamlit as st
import datetime
import random
import pandas as pd
import numpy as np
import serial
import time
import plotly.express as px

# Function to set up the UI elements (logo, header, and system status)
def setup_ui():
    st.sidebar.image("logo.png", width=270)
    st.header("🕒 Feed Time Scheduler")
    st.sidebar.subheader("📊 System Status")

    # Feed status display with descriptive feedback
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

# Function to display advanced settings page
def configure_advanced_settings():
    with st.expander("**⚙️ Advanced Settings**"):
        st.caption("In advanced settings, you can adjust the timeout for feedback and other parameters.")
        
        # Change the base station USB port
        serial_port = st.text_input(r"$\textsf{\normalsize Change the base station USB port:}$", st.session_state.serial_port)
        st.text("")

        # Adjust timeout seconds
        timeout_seconds = st.text_input(r"$\textsf{\normalsize Set custom timeout for feedback (in seconds):}$", st.session_state.timeout_seconds, key="timeout")
        st.text("")
        
        # Choose custom audio file
        audio_file = st.selectbox(r"$\textsf{\normalsize Select custom audio file:}$", ["1", "2", "3"], key="audio")
        st.text("")

        # volume
        volume = st.slider(r"$\textsf{\normalsize Set volume:}$", value=20, min_value=1, max_value=30, step=1)
        st.text("")

        # Choose number of times to play audio file
        play_count = st.slider(r"$\textsf{\normalsize Select number of times to play audio:}$", value=2, min_value=1, max_value=5, step=1)
        st.text("")

        # distance detection
        detection_dist = st.slider(r"$\textsf{\normalsize Set the detection distance (in cm):}$", value=30, min_value=3, max_value=99, step=1)
        st.text("")

        # st.write(f"Selected audio file: {audio_file}")
        # st.write(f"Audio will play {play_count} times.")
        # st.write(f"Volume is set to: {volume}")

        # Save settings
        if st.button('Save Settings', type='primary'):
            st.session_state.serial_port = serial_port
            st.session_state.timeout_seconds = int(timeout_seconds)  # use float(timeout_seconds) if decimals are needed
            st.session_state.audio_file = audio_file
            st.session_state.volume = str(volume)
            st.session_state.play_count = str(play_count)
            st.session_state.detect_dist = str(detection_dist)
            st.success("Settings saved!")

# Function to attempt to establish a serial connection if not already established, or if it failed previously
def init_serial_connection():
    if 'ser' not in st.session_state or not isinstance(st.session_state.ser, serial.Serial) or not st.session_state.ser.is_open:
        try:
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-210', 9600) # tty.usbserial-210 is the port name
            st.info("Serial connection established.")
        except serial.SerialException as e:
            st.error(f"Failed to open serial port: {e}")
            st.session_state.ser = False  # false indicates a failed connection attempt

# Function to initialize required session states (feed time, status, timeout time, audio files) 
def initialize_session_states():
    if 'feed_date' not in st.session_state:
        st.session_state.feed_date = datetime.date.today()
    if 'feed_time' not in st.session_state:
        st.session_state.feed_time = datetime.datetime.now().time()
    if 'feed_status' not in st.session_state:
        st.session_state.feed_status = "Not scheduled"
    if 'serial_port' not in st.session_state:
        st.session_state.serial_port = "/dev/tty.usbserial-210" # default serial port is /dev/tty.usbserial-210
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = "20" # default timeout is 20 seconds
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = "1"       # default audio file is 1st file
    if 'volume' not in st.session_state:
        st.session_state.volume = "20"          # default volume is 20
    if 'play_count' not in st.session_state:
        st.session_state.play_count = "2"       # default number of audio replays is 2
    if 'detect_dist' not in st.session_state:
        st.session_state.detect_dist = "30"     # default detection distance is 30 cm
    if 'activation_times' not in st.session_state:
        st.session_state.activation_times = {}

# Function to send activation command to the feeder
def send_activation_command(feeder_id, is_ball_node):
    command_code = 101 if is_ball_node else 100 # 101 is the custom ID for ball node
    padded_timeout = str(st.session_state.timeout_seconds).zfill(3)
    padded_volume = str(st.session_state.volume).zfill(2)
    padded_play_count = str(st.session_state.play_count).zfill(2)
    padded_detect_dist = str(st.session_state.detect_dist).zfill(2)
    activation_command = str(command_code) + str(padded_timeout) +str(st.session_state.audio_file) + str(padded_volume) + str(padded_play_count) + str(padded_detect_dist) + str(feeder_id)
    print(activation_command)

    if st.session_state.ser:
        try:
            st.session_state.ser.write(activation_command.encode())
            st.sidebar.success(f"Activation command sent to feeder {feeder_id}")
        except Exception as e:
            st.sidebar.error(f"Failed to send activation command to feeder {feeder_id}: {e}")

# Function to wait for feedback from the feeder
def wait_for_feedback(feeder_id):
    expected_prefix_success = f"200{feeder_id}"
    expected_prefix_timeout = f"300{feeder_id}"
    
    while True:
        if st.session_state.ser.in_waiting > 0:
            incoming_data = st.session_state.ser.readline().decode().strip()
            if incoming_data.startswith(expected_prefix_success):
                activation_time = int(incoming_data[len(expected_prefix_success):])
                if feeder_id not in st.session_state.activation_times:
                    st.session_state.activation_times[feeder_id] = []
                st.session_state.activation_times[feeder_id].append(activation_time)
                st.sidebar.success(f"Feedback received from feeder {feeder_id}: {activation_time} seconds")
                with st.container():
                    display_node_activation_stats()
                return activation_time  # Continue collecting times
            elif incoming_data.startswith(expected_prefix_timeout):
                st.sidebar.error(f"Timeout occurred for feeder {feeder_id}")
                return False

# Function to configure feed time / node order
def feed_time_and_node_configuration():
    with st.container(border=True):
      feed_date = st.date_input(r"$\textsf{\large Select feed date:}$", value='today', min_value=datetime.date.today())
      feed_time = st.time_input(r"$\textsf{\large Select feed time:}$", value='now')
      st.session_state.feed_date = feed_date
      st.session_state.feed_time = datetime.datetime.combine(feed_date, feed_time)
    
    st.text("")
    num_nodes = st.slider(r"$\textsf{\large Select the number of nodes to be used:}$", min_value=1, max_value=4, value=2)
    st.caption("If you want to test with 1 node only, choose \'1\' and then \'Custom\' below. If you have 4 nodes in the system, choose up to 4 to be used.")
    st.text("")
    
    with st.container(border=True):
      node_order_choice = st.radio(r"$\textsf{\large Choose the node order method:}$",
                                  ('Random', 'Custom'),
                                  captions = ["Randomly order the nodes according to the number of nodes being used.",
                                              "Write in your own node order. The last node will automatically be the ball node."])
      st.text("")
      if node_order_choice == 'Random':
          iterations = st.number_input(r"$\textsf{\normalsize Select the number of iterations:}$", min_value=1, value=15, step=1)
          st.caption("This represents the number of times you want the bobcat to interact with the nodes before the ball is finally dropped.")
      elif node_order_choice == 'Custom':
          iterations = None  # Not applicable for custom order
    
    return num_nodes, iterations, node_order_choice


# Function to configure data based on the selected node order method (Random or Custom)
def configure_node_data(num_nodes, iterations, node_order_choice):
    initial_node_data = list(range(1, num_nodes + 1))
    sequence = []

    # Random Order
    if node_order_choice == 'Random':
        sequence = create_node_sequence(initial_node_data, iterations, num_nodes)
        random.shuffle(sequence)
        # Automatically set the last node as the ball node
        ball_node_choice = sequence[-1]
    
    # Custom Order
    elif node_order_choice == 'Custom':
        if num_nodes > 1:
          custom_order_input = st.text_input(r"$\textsf{\large Enter the custom node order (comma-separated):}$", ','.join(map(str, initial_node_data)), key="custom_order_input")
          try:
              node_data = [int(i.strip()) for i in custom_order_input.split(',') if i.strip().isdigit()]
              if len(set(node_data)) == num_nodes and all(1 <= n <= num_nodes for n in node_data):
                  # Use the parsed data as the sequence
                  sequence = node_data
                  ball_node_choice = sequence[-1]
              else:
                  st.error("Please enter a valid, unique node order.")
          except ValueError:
              st.error("Please enter numbers only in the node order.")

        else: # num_nodes = 1
            ball_drop = st.toggle("Should this node drop the ball?", value='true', key="ball_node_toggle")
            if (ball_drop):
                ball_node_choice = 1
            else:
                ball_node_choice = None
            sequence = [1]

    return sequence, ball_node_choice

# Function to shuffle node data
def shuffle_node_data(node_data):
    random.shuffle(node_data)
    return node_data

# Function to create node sequence
def create_node_sequence(node_data, iterations, num_nodes):
    sequence = []

    # calculate number of times each node should appear
    node_count = {node: iterations // num_nodes for node in node_data}
    for node in node_data[:iterations % num_nodes]:  # Handle the remainder
        node_count[node] += 1

    # create the sequence by repeating each node by its count
    for node, count in node_count.items():
        sequence.extend([node] * count)

    return sequence

# Function to submit and schedule feeding based on the selected feed time
def submit_and_schedule_feeding(node_data, ball_node_choice):
    # Display current feed information
    display_info(node_data, ball_node_choice)

    # Button to save the scheduled feed time
    if st.button('Schedule Feed Time'):
        # Save feed time, update feed status
        st.session_state.feed_status = "Scheduled"
        st.sidebar.success("Feed time scheduled.")

    # Continuously check if it's time to feed based on the saved feed time
    if 'feed_status' in st.session_state and st.session_state.feed_status == "Scheduled":
        current_datetime = datetime.datetime.now()
        scheduled_datetime = st.session_state.feed_time

        # If current time is greater than scheduled time and feed isn't completed
        if current_datetime >= scheduled_datetime and st.session_state.feed_status != "Completed":
            st.session_state.feed_status = "In Progress"
            init_serial_connection()

            if isinstance(st.session_state.ser, serial.Serial) and st.session_state.ser.is_open:
                activation_times = {}
                for feeder_id in node_data:
                    is_ball_node = (feeder_id == ball_node_choice)
                    send_activation_command(feeder_id, is_ball_node)
                    time_taken = wait_for_feedback(feeder_id)
                    if time_taken is False:  # Check for timeout
                        st.sidebar.error(f"Stopping process. Timeout occurred at feeder {feeder_id}.")
                        st.session_state.feed_status = "Failed"
                        break  # Stop the feeding process
                    elif time_taken is not None:
                        activation_times[feeder_id] = time_taken

                if activation_times and st.session_state.feed_status != "Failed":
                    st.sidebar.success("All feeders activated and feedback received.")
                    st.session_state.feed_status = "Completed"
                elif not activation_times:
                    st.sidebar.warning("No successful activations recorded.")

            else:
                st.sidebar.error("Serial connection not initialized. Cannot send data.")
                st.session_state.feed_status = "Failed"
        elif st.session_state.feed_status != "Completed":
            # If it's not yet time, display a waiting message and plan to check again
            st.sidebar.info("Waiting for the scheduled feed time: " + scheduled_datetime.strftime('%H:%M'))
            time.sleep(1)  # Sleep to avoid continuous loop strain
            st.rerun()


# Function to display feed time and node/ball order information
def display_info(node_data, ball_node_choice):
    feed_time_str = st.session_state.feed_time.strftime('%H:%M')
    node_order = ', '.join(map(str, node_data))
    st.write("Feed time selected is:", feed_time_str)
    st.write("Node order:", node_order)
    if ball_node_choice:
        st.write("Chosen ball node is:", ball_node_choice)
    # st.write("The timeout for each node (in seconds) is:", st.session_state.timeout_seconds, "seconds")
    # st.write("The chosen audio file is:", st.session_state.audio_file)
    # st.write("The volume is set to:", st.session_state.volume)
    st.caption("You can change the timeout, audio file, and volume in the advanced settings.")

# Function to display node activation stats (table and chart)
def display_node_activation_stats():
    st.markdown("---")
    st.subheader("📈 Node Activation Stats")
    
    if st.session_state.activation_times:  # Check if the dictionary is not empty
        # Prepare data for display
        data = []
        for node_id, times in st.session_state.activation_times.items():
            for time in times:
                data.append({"Node": f"Node {node_id}", "Activation Time (s)": time})
        df = pd.DataFrame(data)
        
        # Display activation time table
        styled_df = df.style.format(precision=2) \
            .highlight_max(subset=['Activation Time (s)'], color='lightgreen') \
            .set_properties(**{'text-align': 'center'})
        st.dataframe(styled_df, height=300)
        
        # Display activation time bar chart
        fig = px.bar(df, x='Node', y='Activation Time (s)', text='Activation Time (s)',
                     color='Activation Time (s)', labels={'Activation Time (s)': 'Activation Time (seconds)'},
                     category_orders={"Node": [f"Node {n}" for n in sorted(st.session_state.activation_times.keys())]})
        
        fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': [f"Node {n}" for n in sorted(st.session_state.activation_times.keys())]},
                          yaxis=dict(title='Seconds'), title='Node Activation Times')
        fig.update_traces(texttemplate='%{text}s', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No activation data to display.")  # Display a message if there are no data


# Call functions to run app
initialize_session_states()
setup_ui()
configure_advanced_settings()
num_nodes, iterations, node_order_choice = feed_time_and_node_configuration()
node_data, ball_node_choice = configure_node_data(num_nodes, iterations, node_order_choice)
submit_and_schedule_feeding(node_data, ball_node_choice)