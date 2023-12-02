import streamlit as st
import random
import json

def shuffle_node_data(node_data):
    """
    Shuffle the order of nodes.
    """
    random.shuffle(node_data)
    return node_data

# Streamlit UI
st.header("🕒 Feed Time Scheduler ")
st.divider()

# Settings Section with Emoji
st.subheader("⚙️ Settings ")
# Get feed time from user using a text input
feed_time = st.text_input("Enter feed time (HH : MM):", "13:00")

# Generate number of nodes using a dropdown selector
num_nodes = st.selectbox("Select the number of nodes:", range(4, 8))

# User choice for node order
node_order_choice = st.radio("Choose the node order method:", ('Random', 'Custom'))

# Create node data
node_data = list(range(1, num_nodes + 1))
ball_node_choice = None

if node_order_choice == 'Random':
    shuffle_node_data(node_data)
    ball_node_choice = random.choice(node_data)  # Random ball node when the order is random
else:
    # Allow user to enter custom node order
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

# Randomize button
if st.button('Randomize Node Order and Ball Node'):
    shuffle_node_data(node_data)
    ball_node_choice = random.choice(node_data)

# Divider
st.divider()

# Displaying Selections Section with Emoji
st.subheader("📊 Selections ")
# Display user input for time
if feed_time != "13:00":
    st.write("Your feed time is ", feed_time)

# Display node data as a list of values
st.write("Node order: ", ', '.join(map(str, node_data)))

# Display the selected ball node
if ball_node_choice is not None:
    st.write("Chosen ball node is ", ball_node_choice)

# Submit button to save data to a JSON file
if st.button('Submit and Save Data'):
    data_to_save = {
        "feed_time": feed_time,
        "node_order": node_data,
        "ball_node": ball_node_choice
    }
    with open("feed_time.json", "w") as json_file:
        json.dump(data_to_save, json_file, indent=4)
    st.success("Data saved to feed_time.json")

