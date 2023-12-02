import streamlit as st
import random

def shuffle(node_data):
  for i in range(len(node_data)):
    # generate a random index to swap with
    rand_index = random.randint(0, len(node_data) - 1)
    
    temp = node_data[i]
    node_data[i] = node_data[rand_index]
    node_data[rand_index] = temp
  return node_data


# get feed time from user
feed_time = st.text_input("Enter the feed time (format: hh:mm am/pm):", "Time...")

# display user input
if (feed_time != "Time..."):
  st.write("Your feed time is ", feed_time)

# generate random number of nodes from 4 to 7
num_nodes = st.number_input("Enter the number of nodes:", 4, 7, 4)

# create data structure with num_nodes size
node_data = [0] * num_nodes

for (i, node) in enumerate(node_data):
  node_data[i] = i + 1

# based on num_nodes, randomly order the nodes in node_data
# node_data = [1, 2, 3, 4, ...]
# now, shuffle list
shuffle(node_data)

# pick a random node to be the ball node
ball_node = random.randint(0, len(node_data) - 1)

# display node_data
st.write("Node order is: ", node_data)

# output text file with time, node order, and ball node
# output file name: feed_time.txt
if (feed_time != "Time..."):
  file = open("feed_time.txt", "w")
  file.write("You have selected to feed at " + feed_time + "\n")
  file.write("Node order is " + str(node_data) + "\n")
  file.write("Chosen ball node is " + str(ball_node) + "\n")