# -*- coding: utf-8 -*-
"""Copy of DijkstrasAndAstar.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OMe5mbTI99UY2JxenxIsngqhlkbWCg1m
"""

# Jennifer Chiang, jchiang@cpp.edu, 012639224
# Andy Vu, aavu@cpp.edu, 012264447

"""In this assignment, we will be doing pathfinding using Dijkstra's and A* .  You are provided some starter code below, but the implementation will be up to you. Feel free to create your own sample maps, but you should ensure that your output looks like the final output below.

##In this assignment you will:

* Parse a data file to create a representation of a world-space
* Implement functions that operate over this representation: telling your algorithms how to navigate this space, how to estimate costs over this space, and how to determine when a goal has been reached in this space
* Implement Dijkstra's (an algorithm for finding the optimal path through a graph) search and A* search (a modification of Dijkstra's that utilizes heuristics to speed up the search, while still guaranteeing optimality)

##The goal of this assignment is for you to understand:

* How to read in a data file and produce a representation of the world such that you can generically solve a search problem
* How to implement two basic search algorithms, Dijkstra's and A*
* The differences between Dijkstra's and A*, and why A* is going to be faster than Dijkstra's

First we will load the map into a grid called: terrain

We first use wget to download the file
"""

!wget http://modelai.gettysburg.edu/2019/minecraft/Pathfinding/terrain.txt

"""Now we read from the file"""

with open('terrain.txt','r') as terrain_file:
  terrain = [list(line.rstrip()) for line in terrain_file]
  print('\n'.join([''.join([c for c in row]) for row in terrain]))

"""The indexing on terrain is terrain[y][x].

Now we will implement a `find_neighbors` function.  find_neighbors should take in the curent position (a tuple of `(x,y)`) and the terrain.  It will output a list `[]` of all of the neighbors (tuples of `((x,y), cost)`) the costs are as follows:
🌿 = 1
🌼 = 2
🌉 = 1
🔥 = 5
🌲 = 1

i.e., we are fine walking on grass, bridges, and trees, but would prefer to avoid flowers, and really don't want to swim in lava.

Note: this is assuming a neighborhood of:

🌿🌿🌿

🌿😀🌿

🌿🌿🌿

not

  🌿 
  
🌿😀🌿

  🌿

#Step 1 (20 points)
* Implement the `find_neighbors` function
* It takes in the `current_position` and the `terrain` and returns a list of all locations that are within 1 space 
* For each space it returns the associated cost to move into that space -- the penalty for a movement is incurred when going IN to the space (so if you are on a 🌿 going to a 🌼 then the cost is 2, if you are on a 🌼 going to a 🌿 then the cost is 1)

* Implement the `is_goal` function that returns `True` if the occupied space is the goal, and `False` otherwise
"""

from typing import NamedTuple, Dict, Tuple, Optional, Sequence, List

def find_neighbors(current_position: Tuple[int,int],terrain :List[List[str]]) -> List[Tuple[Tuple[int,int],float]]:
    neighbors = []
    
    # current_position = (x, y)
    # terrain = [y][x] = str 12x10
    # neighbors = [((x, y), cost)]

    all_neighbors = [] # all possible neighbors
    all_neighbors.append((current_position[0], current_position[1] - 1))
    all_neighbors.append((current_position[0], current_position[1] + 1))
    all_neighbors.append((current_position[0] - 1, current_position[1]))
    all_neighbors.append((current_position[0] + 1, current_position[1]))
    all_neighbors.append((current_position[0] - 1, current_position[1] - 1))
    all_neighbors.append((current_position[0] + 1, current_position[1] - 1))
    all_neighbors.append((current_position[0] - 1, current_position[1] + 1))
    all_neighbors.append((current_position[0] + 1, current_position[1] + 1))

    temp = [] # valid possible neighbors
    for i in all_neighbors:
        if (i[0] >= 12) or (i[1] >= 10): # 12x10 map
            continue
        elif (i[0] >= 0) and (i[1] >= 0):
            temp.append(i)

    # append valid neighbors with cost to list
    # 🌿, 🌉, 🌲 = 1 
    # 🌼 = 2 
    # 🔥 = 5
    for i in temp: 
        if terrain[i[1]][i[0]] == "🌿" or terrain[i[1]][i[0]] == "🌉" or terrain[i[1]][i[0]] == "🌲":
            neighbors.append((i, 1.0))
        elif terrain[i[1]][i[0]] == "🌼":
            neighbors.append((i, 2.0))
        elif terrain[i[1]][i[0]] == "🔥":
            neighbors.append((i, 5.0))

    return neighbors
# call to test find_neighbors method
# print(find_neighbors((3,3), terrain))
    
def is_goal(current_position: Tuple[int,int],terrain :List[List[str]]) -> bool:
    goal = False
    # terrain is [y][x]
    x = current_position[0]
    y = current_position[1]
    position = terrain[y][x]
    if(position == "🌲"):
      goal = True
    return goal
# call to test is_goal method
# print(is_goal((11,9), terrain))

"""Now, we want to find the heuristic cost for a given location on the terrain.  The heuristic cost you should use is:

Find the Euclidean distance to the nearest 🌲 -- e.g. if the tree is at (x',y') and the given location is (x,y) the heuristic distance is $\sqrt{(y-y')^2 + (x-x')^2}$
# Step 2 (15 points)
* Fill in the heuristic function
* It should return the Euclidean distance to the CLOSEST tree, not just any tree
"""

import math

def get_heuristic(position : Tuple[int,int],terrain:List[List[str]]) -> float:
    min_distance = 0
    
    tree_locations = [] # all locations of trees
    for y in range(len(terrain)):
        for x in range(len(terrain[y])):
            if terrain[y][x] == "🌲":
                tree_locations.append((x, y))

    for i in tree_locations:
        temp = math.sqrt(((position[1] - i[1])**2) + ((position[0] - i[0])**2))
        if (min_distance == 0) or (min_distance > temp):
            min_distance = temp

    return min_distance

"""Finally, here is a helper class -- `PriorityQueue` -- and a helper function `pretty_print_path` that takes in the path (a list of position (x,y) tuples) and outputs a pretty string with emoji showing the path through the terrain

To use the priority queue, you must first instantiate it, then use `put` to add things in and `get` to retrieve them
"""

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority : float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]
    
def pretty_print_path(path : List[Tuple[int,int]], terrain :List[List[str]]):
        
    emojis = ['😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋']
    
    path2len = {location:distance for distance,location in enumerate(path)}
    output = []
    for yy,row in enumerate(terrain):
        row_str = ''
        for xx, cur in enumerate(row):
            if (xx,yy) in path2len:
                row_str += emojis[path2len[(xx,yy)] % len(emojis)]
            else:
                row_str += cur
        output.append(row_str)
    return '\n'.join(output)

"""#STEP 3 (Dijkstra's -- 25 points -- A* -- 40 points)
* Implement both Dijkstra's and A*
* The functions should use the early stopping criteria -- but make sure you stop at the right point
* If no path can be found, then you should return an empty list
* If a path is found, then you should return a list of tuples of ints 
* The returned path should be in the correct order (start to finish)

You should verify a few things

1) Your results for Dijkstra's and A* should be the same

2) If you run A\* with a heuristic of  lambda pos: 0, then your Dijkstra's implementation should visit things in the same order as your A\*

3) A* should likely visit fewer nodes than Dijkstra's
"""

def dijkstras(initial_position : Tuple[int,int], world : List[List[str]],get_neighbors , is_goal) -> List[Tuple[int,int]]:
    result = []
    # instantiating the priority queue
    pq = PriorityQueue() 
    print(pq.empty())
    
    return result

def a_star(initial_position,world,get_neighbors,is_goal,heuristic):
    open_list = []
    closed_list = []

    
    
    return []

"""Your final output -- after pretty printing your paths should look like:
    
😀🌿🌿🌿🌿🌼🌿🌼🌼🌿🌿🌿

🌿😁🌿🌿🌿🌼😅🌼🌼🌿🌿🌿

🌿🌿😂🤣😃😄🌼😆🌿🌿🌿🌿

🌿🌿🌿🌊🌊🌊🌊🌊😉🌊🌊🌊

🌊🌊🌊🌊🌊🌊🌊🌊😊🌊🌊🌊

🌊🌊🌊🌊🌊🌊🌊🌊😋🌊🌊🌊

🌊🌊🌊🌊🌊🌊🌊🌊😀🌊🌊🌊

🌊🌊🌊🌊🌊🌊🌊🌊😁🌊🌊🌊

🌊🌊🌊🌊🌊🌊🌊🌊😂🌊🌊🌊

🌿🌿🌿🌲🌿🌿🌿🌿🌿🤣😃🌲
"""

dijkstra_path = dijkstras((0,0), terrain, find_neighbors, is_goal )
print('Dijkstras')
print(pretty_print_path(dijkstra_path, terrain))

a_star_path = a_star((0,0), terrain, find_neighbors, is_goal,get_heuristic )
print('A*')
print(pretty_print_path(a_star_path, terrain))

"""#Bonus!

* Make a new map that is either fun in some special way, or has a somewhat surprising best path (1 pt)
* Modify the terrain to have a new terrain type with a different cost (2 pts)
"""

