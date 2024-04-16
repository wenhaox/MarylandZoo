import serial
import streamlit as st
import datetime
import random
import pandas as pd
import numpy as np
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
        st.session_state.feed_time = datetime.datetime.now().time()
    if 'feed_status' not in st.session_state:
        st.session_state.feed_status = "Not scheduled"
    if 'timeout_seconds' not in st.session_state:
        st.session_state.timeout_seconds = "20" # default timeout is 20 seconds
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = "audio1.mp3"

# Function to send activation command to the feeder
def send_activation_command(feeder_id, is_ball_node):
    command_code = 101 if is_ball_node else 100 # 101 is the custom ID for ball node
    
    activation_command = str(command_code) + str(feeder_id)
    if st.session_state.ser:
        try:
            st.session_state.ser.write(activation_command.encode())
            st.sidebar.success(f"Activation command sent to feeder {feeder_id}")
        except Exception as e:
            st.sidebar.error(f"Failed to send activation command to feeder {feeder_id}: {e}")

# Function to wait for feedback from the feeder
def wait_for_feedback(feeder_id, is_ball_node):
    feedback_code = 2000
    expected_feedback = str(feedback_code + feeder_id)
    feedback_received = False
    start_time = time.time()
    timeout_seconds = int(st.session_state.timeout_seconds)  # use float() for decimal values
    
    while not feedback_received and (time.time() - start_time) < timeout_seconds:
        if st.session_state.ser.in_waiting > 0:
            incoming_data = st.session_state.ser.readline().decode().strip()
            print(f"Received: {incoming_data}, Expected: {expected_feedback}")
            if incoming_data == expected_feedback:
                st.sidebar.success(f"Feedback received from feeder {feeder_id}")
                feedback_received = True
            else:
                # st.error(f"Unexpected feedback received: {incoming_data}")
                pass
        time.sleep(0.1)  # sleep to avoid busy waiting
    
    if not feedback_received:
        st.sidebar.error(f"Timeout waiting for feedback from feeder {feeder_id}")

def feed_time_and_node_configuration():
    feed_time = st.time_input("Select feed time:", st.session_state.feed_time)
    st.session_state.feed_time = feed_time
    num_nodes = st.slider("Select the number of nodes:", min_value=2, max_value=4, value=2)
    iterations = st.number_input("Select the number of iterations:", min_value=1, value=15, step=1)
    node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))
    return num_nodes, iterations, node_order_choice

# Function to configure data based on the selected node order method (Random or Custom)
def configure_node_data(num_nodes, iterations, node_order_choice):
    initial_node_data = list(range(1, num_nodes + 1))
    sequence = []

    if node_order_choice == 'Random':
        # assuming no iterations
        # node_data, ball_node_choice = process_random_order(node_data)
        
        # assuming with iterations
        ball_node_choice = st.selectbox("Select the node that will have the ball:", list(range(1, num_nodes + 1)), key="random_ball_node")
        # create sequence, shuffle data
        sequence = create_node_sequence(initial_node_data, iterations, num_nodes)
        shuffle_node_data(sequence)
        # make sure ball node is the last node
        if ball_node_choice in sequence:
            sequence.remove(ball_node_choice)
        sequence.append(ball_node_choice)
            
    else:
        custom_order = st.text_input("Enter the custom node order (comma-separated):", ','.join(map(str, initial_node_data)))
        # assuming no iterations
        node_data, ball_node_choice = process_custom_order(custom_order, num_nodes)
        ball_node_choice = st.selectbox("Select the node that will have the ball:", list(range(1, num_nodes + 1)), key="custom_ball_node")
        
        # parse user input and validate
        node_data = [int(i.strip()) for i in custom_order.split(',')]
        if (len(set(node_data)) == num_nodes) and all(1 <= n <= num_nodes for n in node_data):
            if ball_node_choice:
                node_data.remove(ball_node_choice)
                node_data.append(ball_node_choice)
        else:
            st.error("Please enter a valid, unique node order.")
            node_data = list(range(1, num_nodes + 1))
            ball_node_choice = None
        
        sequence = create_node_sequence(node_data, iterations, num_nodes)
    # return node_data, locals().get('ball_node_choice')
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

# Function to submit and schedule feeding based on the selected feed time
def submit_and_schedule_feeding(node_data, ball_node_choice):
    # display current feed information
    display_info(node_data, ball_node_choice)
    
    # button to save the scheduled feed time
    if st.button('Schedule Feed Time'):
        # save feed time, update feed status
        st.session_state.feed_status = "Scheduled"
        st.sidebar.success("Feed time scheduled.")
    
    # keep listening to check if it's time to feed based on the saved feed time
    if 'feed_status' in st.session_state and st.session_state.feed_status == "Scheduled":
        current_time = datetime.datetime.now().time()
        scheduled_time = st.session_state.feed_time
        
        # if curr time is greater than scheduled time and feed isn't completed
        if current_time >= scheduled_time and st.session_state.feed_status != "Completed":
            st.session_state.feed_status = "In Progress"
            init_serial_connection()
            
            # check if serial connection is properly initialized
            if isinstance(st.session_state.ser, serial.Serial) and st.session_state.ser.is_open:
                try:
                    # iterate through each node to send the custom activation command and wait for feedback
                    for feeder_id in node_data:
                        is_ball_node = (feeder_id == ball_node_choice)
                        send_activation_command(feeder_id, is_ball_node)
                        wait_for_feedback(feeder_id, is_ball_node)
                    st.sidebar.success("All feeders activated and feedback received.")
                    st.session_state.feed_status = "Completed"
                except Exception as e:
                    st.sidebar.error(f"Failed to activate feeders: {e}")
                    st.session_state.feed_status = "Failed"
            else:
                st.sidebar.error("Serial connection not initialized. Cannot send data.")
                st.session_state.feed_status = "Failed"
        elif st.session_state.feed_status != "Completed":
            # if it's not yet time, display a waiting message and plan to check again
            st.sidebar.info("Waiting for the scheduled feed time: " + scheduled_time.strftime('%H:%M'))
            time.sleep(1)  # sleep because we don't need to check continuously
            st.rerun()

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
def display_node_activation_stats(node_data):
    st.markdown("---")
    st.subheader("📈 Node Activation Stats")
    activation_times = np.random.randint(1, 15, size=len(node_data))
    df = pd.DataFrame({
        'Node': ['Node ' + str(node) for node in node_data],
        'Activation Time (s)': activation_times
    })

    # Activation time table
    styled_df = df.style.format(precision=2) \
        .highlight_max(subset=['Activation Time (s)'], color='lightgreen') \
        .set_properties(**{'text-align': 'center'})
    st.dataframe(styled_df, height=300)

    # Activation time bar chart
    fig = px.bar(df, x='Node', y='Activation Time (s)', text='Activation Time (s)',
                 color='Activation Time (s)', labels={'Activation Time (s)': 'Activation Time (seconds)'},
                 category_orders={"Node": [f"Node {n}" for n in node_data]})  # Use the user-defined order for categories

    fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': [f"Node {n}" for n in node_data]}, 
                      yaxis=dict(title='Seconds'), title='Node Activation Times')
    fig.update_traces(texttemplate='%{text}s', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# Call functions to run app
initialize_session_states()
setup_ui()
configure_advanced_settings()
num_nodes, iterations, node_order_choice = feed_time_and_node_configuration()
node_data, ball_node_choice = configure_node_data(num_nodes, iterations, node_order_choice)
submit_and_schedule_feeding(node_data, ball_node_choice)
display_node_activation_stats(node_data)