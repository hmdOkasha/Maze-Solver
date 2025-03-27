import streamlit as st
import numpy as np
import scipy.io
from collections import deque
import matplotlib.pyplot as plt
import time

def get_neighbors_8(row, col, rows, cols):
    deltas = [
        (-1, 0),  # Up
        (0, 1),   # Right
        (1, 0),   # Down
        (0, -1),  # Left
        (-1, 1),  # Up-Right
        (1, 1),   # Down-Right
        (1, -1),  # Down-Left
        (-1, -1)  # Up-Left
    ]
    
    for dRow, dCol in deltas:
        newRow, newCol = row + dRow, col + dCol
        if 0 <= newRow < rows and 0 <= newCol < cols:
            yield newRow, newCol
            
def wavefront_expansion(map_, goal_row, goal_col):
    rows = len(map_)
    cols = len(map_[0])
    value_map = [[map_[i][j] for j in range(cols)] for i in range(rows)]
    queue = deque()
    value_map[goal_row][goal_col] = 2
    queue.append((goal_row, goal_col))
    
    while queue:
        row, col = queue.popleft()
        for newRow, newCol in get_neighbors_8(row, col, rows, cols):
            if value_map[newRow][newCol] == 0:
                value_map[newRow][newCol] = value_map[row][col] + 1
                queue.append((newRow, newCol))
    
    return value_map

def get_path(value_map, start_row, start_col):
    rows = len(value_map)
    cols = len(value_map[0])
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return []
    if value_map[start_row][start_col] == 0:
        return []
    
    path = []
    row, col = start_row, start_col
    path.append((row, col))
    
    while value_map[row][col] != 2:
        current_value = value_map[row][col]
        best_neighbor = None
        best_value = current_value
        for newRow, newCol in get_neighbors_8(row, col, rows, cols):
            if value_map[newRow][newCol] < best_value and value_map[newRow][newCol] != 1 and value_map[newRow][newCol] > 0:
                best_neighbor = (newRow, newCol)
                best_value = value_map[newRow][newCol]
        if best_neighbor is None:
            break
        row, col = best_neighbor
        path.append((row, col))
    
    return path

def planner(map_, start_row, start_col):
    # Validate starting position
    rows = len(map_)
    cols = len(map_[0])
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        raise ValueError(f"Starting position ({start_row}, {start_col}) is outside the map boundaries. Please choose coordinates within the range: row [0-{rows-1}], col [0-{cols-1}]")
    
    if map_[start_row][start_col] == 1:
        raise ValueError(f"Starting position ({start_row}, {start_col}) is on a wall. Please choose a free space position (value 0)")
    
    goal_found = False
    for i in range(len(map_)):
        for j in range(len(map_[0])):
            if map_[i][j] == 2:
                goal_found = True
                goal_row = i
                goal_col = j
                break
        if goal_found:
            break
    if not goal_found:
        raise ValueError("Goal not found in the map")
    
    value_map = wavefront_expansion(map_, goal_row, goal_col)
    path = get_path(value_map, start_row, start_col)
    return value_map, path, (goal_row, goal_col)

def show_map_and_path(value_map, path, goal_pos):
    arr = np.array(value_map)
    fig, ax = plt.subplots(figsize=(8, 6))
    arr_plot = np.copy(arr)
    arr_plot[arr_plot == 1] = -1  # obstacles
    im = ax.imshow(arr_plot, cmap='viridis', origin='lower')  # Changed to 'lower' to start from top
    
    # Plot the goal point
    goal_row, goal_col = goal_pos
    ax.plot(goal_col, goal_row, 'go', markersize=10, label='Goal')
    
    if path:
        # Plot complete path
        tr_rows = [p[0] for p in path]
        tr_cols = [p[1] for p in path]
        ax.plot(tr_cols, tr_rows, 'r-', linewidth=1, label='Path')
        # Plot start point
        ax.plot(tr_cols[0], tr_rows[0], 'ro', markersize=5, label='Start')
    
    plt.colorbar(im, label="Wavefront Value (obstacles in black)")
    ax.legend()
    return fig

def display_path_matrix(path):
    st.subheader("Path Coordinates")
    
    # Calculate number of columns for the matrix display
    num_cols = 5  # You can adjust this number
    num_steps = len(path)
    
    # Create rows of steps
    for i in range(0, num_steps, num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < num_steps:
                step_num = i + j + 1
                row, col = path[i + j]
                cols[j].write(f"Step {step_num}: ({row}, {col})")

def main():
    st.title("Wavefront Path Planner")
    st.write("Upload a .mat file containing a maze map and specify the starting position to find the path to the goal.")

    # File upload
    uploaded_file = st.file_uploader("Choose a .mat file", type=['mat'])
    
    if uploaded_file is not None:
        try:
            mat_data = scipy.io.loadmat(uploaded_file)
            map_data = mat_data['map']
            if isinstance(map_data, np.ndarray):
                map_data = map_data.tolist()
            
            # Display the original map
            st.subheader("Original Map")
            fig_original = plt.figure(figsize=(8, 6))
            plt.imshow(map_data, cmap='binary', origin='lower')  # Changed to 'lower' to start from top
            plt.colorbar(label="Obstacles (1) / Free Space (0)")
            st.pyplot(fig_original)
            
            # Input fields for starting position
            col1, col2 = st.columns(2)
            with col1:
                start_row = st.number_input("Starting Row", min_value=0, max_value=len(map_data)-1, value=0)
            with col2:
                start_col = st.number_input("Starting Column", min_value=0, max_value=len(map_data[0])-1, value=0)
            
            # Show current selection on map
            st.write(f"Selected starting position: ({start_row}, {start_col})")
            if map_data[start_row][start_col] == 1:
                st.warning("⚠️ Warning: Selected position is on a wall. Please choose a free space position (value 0)")
            else:
                st.success("✅ Selected position is valid (free space)")
            
            if st.button("Find Path"):
                try:
                    # Start timing
                    start_time = time.time()
                    
                    value_map, path, goal_pos = planner(map_data, start_row, start_col)
                    
                    # Calculate computation time
                    computation_time = time.time() - start_time
                    
                    # Display computation time
                    st.success(f"Path found in {computation_time:.4f} seconds")
                    
                    # Display the value map and path
                    st.subheader("Value Map and Path")
                    fig = show_map_and_path(value_map, path, goal_pos)
                    st.pyplot(fig)
                    
                    # Display the value map matrix
                    st.subheader("Value Map Matrix")
                    value_map_array = np.array(value_map)
                    st.dataframe(value_map_array, use_container_width=True)
                    
                    # Display path coordinates in matrix format
                    display_path_matrix(path)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    main()