### Analysis-In current setting we do not consider agent "turning" towards the direction which it chooses to move. Based on the previous assignment how would you propose to fix this short-coming in the context of the search problem we are solving?

How do you propose to consider turning effort to be added to the cost? How does your proposed solution affect the branching factor and the number of nodes being added to the frontier at each step? How do you think your strategy will affect the chosen path at each search? Finally come up with a pseudocode describing how to implement this at search and at the visual rendering part. This part of the assignment worth 15%. Feel free to attach a couple of pages answering these questions along with any drawing if you think would describe your solution better. 
A bonus mark will be if you implement your above proposed solution for one of the search algorithms above. If you choose to do this bonus part, I suggest add a button or option in the search list to be able to select the search with turn. For example if you choose to add it to BFS, then add an option to the list of searches named BFS_Turn for example. The bonus mark with be 5%.


#### Answer


To address the shortcoming of not considering turning in the agent's movement, we can modify the search problem by including the agent's orientation as part of the state. This way, the agent's current position and orientation will be considered when choosing the next action.

To incorporate turning effort into the cost, we can assign a higher cost to actions that involve changing the agent's orientation. For example, we can assign a cost of 1 to "Forward" actions and a cost of 2 to "TurnLeft" or "TurnRight" actions. This reflects the additional effort required to change the orientation.

Considering turning effort will increase the branching factor at each step. Previously, the agent had four options (UP, DOWN, LEFT, RIGHT) regardless of its orientation. Now, the agent's orientation affects the available actions. For example, if the agent is facing north, it can choose between moving UP, LEFT, or RIGHT but not DOWN. This increases the number of possible actions at each state.

As a result, the number of nodes being added to the frontier at each step will also increase. The increased branching factor means more potential paths to explore, leading to a larger frontier in the search algorithm.

The effect of considering turning effort on the chosen path will depend on the specific search algorithm used. In general, taking turning effort into account can lead to paths that minimize the number of turns or prioritize more efficient movements.

Here's a pseudocode outlining the implementation of this approach:

```
function searchWithTurn(problem):
    initialize the frontier with the initial state
    initialize an empty set of explored states
    
    while frontier is not empty:
        current_state = remove state from frontier
        
        if current_state is the goal state:
            return the path to the current_state
        
        add current_state to explored states
        
        for each action in possible_actions:
            next_state = apply action to current_state
            
            if next_state is not in explored states or frontier:
                add next_state to the frontier
                set the cost of reaching next_state to the cost of current_state plus the action cost
            
            else if next_state is in the frontier with higher cost:
                replace the existing state with next_state and update the cost
        
    return failure (no path found)
```