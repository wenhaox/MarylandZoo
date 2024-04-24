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
    with st.expander("⚙️ Advanced Settings"):
        st.caption("In advanced settings, you can adjust the timeout for feedback and other parameters.")
        
        # Adjust timeout seconds
        timeout_seconds = st.text_input("Set custom timeout for feedback (in seconds):", st.session_state.timeout_seconds, key="timeout")
        
        # Choose custom audio file
        audio_file = st.selectbox("Select custom audio file:", ["audio1.mp3", "audio2.mp3", "audio3.mp3"], key="audio")
        st.write(f"Selected audio file: {audio_file}")

        # Choose number of times to play audio file
        play_count = st.slider("Select number of times to play audio:", 1, 5, 1)
        st.write(f"Audio will play {play_count} times.")

        # Save settings
        if st.button('Save Settings'):
            st.session_state.timeout_seconds = int(timeout_seconds)  # use float(timeout_seconds) if decimals are needed
            st.session_state.audio_file = audio_file
            st.success("Settings saved!")

# Function to attempt to establish a serial connection if not already established, or if it failed previously
def init_serial_connection():
    if 'ser' not in st.session_state or not isinstance(st.session_state.ser, serial.Serial) or not st.session_state.ser.is_open:
        try:
            st.session_state.ser = serial.Serial('/dev/tty.usbserial-210', 9600)
            st.info("Serial connection established.")
        except serial.SerialException as e:
            st.error(f"Failed to open serial port: {e}")
            st.session_state.ser = False  # false indicates a failed connection attempt

# Function to initialize required session states (feed time, status, timeout time, audio files) 
def initialize_session_states():
    if 'feed_time' not in st.session_state:
        st.session_state.feed_time = datetime.datetime.now()
    if 'feed_date' not in st.session_state:
        st.session_state.feed_date = datetime.date.today()
    if 'feed_status' not in st.session_state:
        st.session_state.feed_status = "Not scheduled"
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = "20" # default timeout is 20 seconds
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = "audio1.mp3"
    
# Function to send activation command to the feeder
def send_activation_command(feeder_id, is_ball_node):
    command_code = 101 if is_ball_node else 100 # 101 is the custom ID for ball node
    padded_timeout = str(st.session_state.timeout_seconds).zfill(3)
    activation_command = str(command_code) + str(padded_timeout) + str(feeder_id)
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
    activation_time = None

    while True:
        if st.session_state.ser.in_waiting > 0:
            incoming_data = st.session_state.ser.readline().decode().strip()
            if incoming_data.startswith(expected_prefix_success):
                # Extract the time taken, which is the rest of the string after the prefix
                activation_time = int(incoming_data[len(expected_prefix_success):])
                st.sidebar.success(f"Feedback received from feeder {feeder_id}: {activation_time} seconds")
                return activation_time  # Return the actual time for processing
            elif incoming_data.startswith(expected_prefix_timeout):
                st.sidebar.error(f"Timeout occurred for feeder {feeder_id}")
                st.session_state.feed_status = "Failed"
                return None  # Return None to indicate a timeout

def feed_time_and_node_configuration():
    # Allow users to select both date and time with session state values as defaults
    if 'feed_date' not in st.session_state:
        st.session_state.feed_date = datetime.date.today()
    if 'feed_time' not in st.session_state:
        st.session_state.feed_time = datetime.datetime.now().time()

    feed_date = st.date_input("Select feed date:", value='today')
    feed_time = st.time_input("Select feed time:", value='now')

    
    # Update the session state with the new date and time
    st.session_state.feed_date = feed_date
    st.session_state.feed_time = datetime.datetime.combine(feed_date, feed_time)

    num_nodes = st.slider("Select the number of nodes:", min_value=2, max_value=4, value=2)
    node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))
    
    if node_order_choice == 'Random':
        iterations = st.number_input("Select the number of iterations:", min_value=1, value=15, step=1)
    else:
        iterations = None  # Not applicable for custom order
    
    return num_nodes, iterations, node_order_choice

# Function to configure data based on the selected node order method (Random or Custom)
def configure_node_data(num_nodes, iterations, node_order_choice):
    initial_node_data = list(range(1, num_nodes + 1))
    sequence = []

    if node_order_choice == 'Random':
        sequence = create_node_sequence(initial_node_data, iterations, num_nodes)
        random.shuffle(sequence)
        # Automatically set the last node as the ball node
        ball_node_choice = sequence[-1]
    else:
        custom_order_input = st.text_input("Enter the custom node order (comma-separated):", ','.join(map(str, initial_node_data)), key="custom_order_input")
        try:
            node_data = [int(i.strip()) for i in custom_order_input.split(',') if i.strip().isdigit()]
            if len(set(node_data)) == num_nodes and all(1 <= n <= num_nodes for n in node_data):
                # Use the parsed data as the sequence
                sequence = node_data
                # Automatically set the last node as the ball node
                ball_node_choice = sequence[-1]
            else:
                st.error("Please enter a valid, unique node order.")
        except ValueError:
            st.error("Please enter numbers only in the node order.")

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

# Function for random order input
def process_random_order(node_data):
    node_data = shuffle_node_data(node_data)
    # give user the option to either select the ball node or have it randomly chosen
    ball_node_choice = st.selectbox("Select the node that will have the ball:", list(range(1, len(node_data) + 1)), key="custom_ball_node")
    if ball_node_choice:
        node_data.remove(ball_node_choice)
        node_data.append(ball_node_choice) # ensures the ball node appears at the end
    return node_data, ball_node_choice

# Function for custom order input
def process_custom_order(custom_order, num_nodes):
    try:
        # parse user input and validate
        node_data = [int(i.strip()) for i in custom_order.split(',')]
        if (len(set(node_data)) == num_nodes) and all(1 <= n <= num_nodes for n in node_data):
            ball_node_choice = st.selectbox("Select the node that will have the ball:", list(range(1, num_nodes + 1)))
            if ball_node_choice:
                node_data.remove(ball_node_choice)
                node_data.append(ball_node_choice)
            return node_data, ball_node_choice
        else:
            st.error("Please enter a valid, unique node order.")
            return list(range(1, num_nodes + 1)), None
    except ValueError:
        st.error("Please enter numbers only in the node order.")
        return list(range(1, num_nodes + 1)), None

def submit_and_schedule_feeding(node_data, ball_node_choice):
    display_info(node_data, ball_node_choice)
    
    if st.button('Schedule Feed Time'):
        # Save feed time and update feed status
        st.session_state.feed_status = "Scheduled"
        st.sidebar.success("Feed time scheduled.")

    # Continuously check if it's time to feed based on the saved feed time
    if 'feed_status' in st.session_state and st.session_state.feed_status == "Scheduled":
        current_datetime = datetime.datetime.now()
        scheduled_datetime = st.session_state.feed_time
        
        if current_datetime >= scheduled_datetime and st.session_state.feed_status != "Completed":
            st.session_state.feed_status = "In Progress"
            init_serial_connection()

            if isinstance(st.session_state.ser, serial.Serial) and st.session_state.ser.is_open:
                activation_times = {}
                for feeder_id in node_data and st.session_state.feed_status == "Scheduled":
                    is_ball_node = (feeder_id == ball_node_choice)
                    send_activation_command(feeder_id, is_ball_node)
                    time_taken = wait_for_feedback(feeder_id)
                    if time_taken is not None:
                        activation_times[feeder_id] = time_taken

                if activation_times:
                    st.sidebar.success("All feeders activated and feedback received.")
                    display_node_activation_stats(activation_times)
                else:
                    st.sidebar.warning("No successful activations recorded.")
                
                st.session_state.feed_status = "Completed"
            else:
                st.sidebar.error("Serial connection not initialized. Cannot send data.")
                st.session_state.feed_status = "Failed"
        elif st.session_state.feed_status != "Completed":
            st.sidebar.info("Waiting for the scheduled feed time: " + scheduled_datetime.strftime('%H:%M'))
            time.sleep(5)  # This sleep is critical to prevent continuous loop execution which can hang the app
            st.experimental_rerun()


# Function to display feed time and node/ball order information
def display_info(node_data, ball_node_choice):
    feed_time_str = st.session_state.feed_time.strftime('%H:%M')
    node_order = ', '.join(map(str, node_data))
    st.write("Feed time selected is:", feed_time_str)
    st.write("Node order:", node_order)
    if ball_node_choice:
        st.write("Chosen ball node is:", ball_node_choice)
    st.write("The timeout for each node (in seconds) is:", st.session_state.timeout_seconds, "seconds")
    st.caption("You can change this timeout number in the advanced settings.")

# Function to display node activation stats (table and chart)
def display_node_activation_stats(activation_times):
    st.markdown("---")
    st.subheader("📈 Node Activation Stats")

    if activation_times:  # Check if the activation_times dictionary is not empty
        # Prepare data for display
        data_items = [{"Node": f"Node {node_id}", "Activation Time (s)": time} for node_id, time in activation_times.items()]
        df = pd.DataFrame(data_items)

        # Activation time table
        styled_df = df.style.format(precision=2) \
            .highlight_max(subset=['Activation Time (s)'], color='lightgreen') \
            .set_properties(**{'text-align': 'center'})
        st.dataframe(styled_df, height=300)

        # Activation time bar chart
        fig = px.bar(df, x='Node', y='Activation Time (s)', text='Activation Time (s)',
                     color='Activation Time (s)', labels={'Activation Time (s)': 'Activation Time (seconds)'},
                     category_orders={"Node": [f"Node {n}" for n in activation_times.keys()]})

        fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': [f"Node {n}" for n in activation_times.keys()]},
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