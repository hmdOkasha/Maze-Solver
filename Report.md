# Wavefront Path Planner - Implementation Report

## 1. User Interface Overview

### 1.1 Initial Setup
The application starts with a simple interface where users can:
- Upload a .mat file containing the maze map
- View the original map visualization where:
  - Grey/Black areas represent walls or obstacles (value 1)
  - White areas represent free space (value 0)
  - Green dot represents the goal position (value 2)

### 1.2 Path Planning Process
After uploading the map, users can:
1. Select starting coordinates using number input fields
2. Get immediate feedback about their selection:
   - Warning if selected position is on a wall
   - Success message if position is valid
3. Click "Find Path" to generate the solution
4. View multiple visualizations:
   - Value map with path overlay
   - Heat map showing wavefront expansion
   - Matrix representation of the value map
   - Step-by-step path coordinates

## 2. Code Implementation

### 2.1 Core Functions

#### get_neighbors_8(row, col, rows, cols)
```python
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
```
This function implements the 8-directional movement pattern required for the wavefront algorithm. It:
- Takes current position (row, col) and map dimensions
- Returns valid neighboring positions in priority order
- Ensures neighbors are within map boundaries

#### wavefront_expansion(map_, goal_row, goal_col)
```python
def wavefront_expansion(map_, goal_row, goal_col):
    value_map = [[map_[i][j] for j in range(cols)] for i in range(rows)]
    queue = deque()
    value_map[goal_row][goal_col] = 2
    queue.append((goal_row, goal_col))
```
This function implements the core wavefront algorithm:
1. Initializes value map from original map
2. Sets goal position value to 2
3. Uses breadth-first search to expand wavefront
4. Assigns increasing values to free spaces
5. Maintains priority order in expansion

#### get_path(value_map, start_row, start_col)
```python
def get_path(value_map, start_row, start_col):
    path = []
    row, col = start_row, start_col
    path.append((row, col))
```
This function finds the optimal path by:
1. Starting from given position
2. Following decreasing values to goal
3. Using 8-directional movement
4. Avoiding obstacles
5. Returning list of path coordinates

#### planner(map_, start_row, start_col)
```python
def planner(map_, start_row, start_col):
    # Validate starting position
    # Find goal position
    value_map = wavefront_expansion(map_, goal_row, goal_col)
    path = get_path(value_map, start_row, start_col)
```
This is the main planning function that:
1. Validates input parameters
2. Finds goal position in map
3. Calls wavefront expansion
4. Generates path
5. Returns complete solution

### 2.2 Visualization Functions

#### show_map_and_path(value_map, path, goal_pos)
```python
def show_map_and_path(value_map, path, goal_pos):
    arr = np.array(value_map)
    fig, ax = plt.subplots(figsize=(8, 6))
```
This function creates visualizations:
1. Converts value map to numpy array
2. Creates heat map visualization
3. Plots goal point (green)
4. Plots path (red line)
5. Plots start point (red dot)
6. Adds legend and colorbar

#### display_path_matrix(path)
```python
def display_path_matrix(path):
    num_cols = 5
    num_steps = len(path)
```
This function creates a matrix display of path coordinates:
1. Shows 5 steps per row
2. Numbers steps sequentially
3. Displays row and column coordinates
4. Makes path easy to follow

### 2.3 Main Application

The main function implements the Streamlit interface:
1. File upload handling
2. Map visualization
3. User input validation
4. Path computation
5. Results display
6. Error handling

## 3. Algorithm Details

### 3.1 Wavefront Expansion
The algorithm follows these steps:
1. Initialize goal position with value 2
2. Expand to neighboring free spaces
3. Assign increasing values (3, 4, 5, etc.)
4. Continue until all reachable spaces are filled
5. Maintain priority order: Up, Right, Down, Left, Up-Right, Down-Right, Down-Left, Up-Left

### 3.2 Path Finding
The path is found by:
1. Starting from given position
2. Following decreasing values
3. Moving to neighbor with lowest value
4. Continuing until goal is reached
5. Avoiding obstacles and unreachable spaces

## 4. Performance Considerations

The implementation includes:
1. Input validation
2. Error handling
3. Computation time measurement
4. Efficient data structures (deque for queue)
5. Optimized neighbor checking

## 5. Future Improvements

Potential enhancements could include:
1. Multiple goal support
2. Different movement patterns
3. Path optimization
4. Interactive map creation
5. Path animation options 