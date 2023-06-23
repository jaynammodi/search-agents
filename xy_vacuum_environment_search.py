import os.path
from tkinter import *
from agents import *
from search import *
import sys
import copy
import math
from utils import PriorityQueue
import time

"""
1- BFS: Breadth first search. Using tree or graph version, whichever makes more sense for the problem
2- DFS: Depth-First search. Again using tree or graph version.
3- UCS: Uniform-Cost-Search. Using the following cost function to optimise the path, from initial to current state.
4- A*:  Using A star search.
"""
searchTypes = ['None', 'BFS', 'DFS', 'UCS', 'A*']


class VacuumPlanning(Problem):
    """ The problem of find the next room to clean in a grid of m x n rooms.
    A state is represented by state of the grid. Each room is specified by index set
    (i, j), i in range(m) and j in range (n). Final goal is to find all dirty rooms. But
     we go by sub-goal, meaning finding next dirty room to clean, at a time."""

    def __init__(self, env, searchtype):
        """ Define goal state and initialize a problem
            initial is a pair (i, j) of where the agent is
            goal is next pair(k, l) where map[k][l] is dirty
        """
        self.solution = None
        self.env = env
        self.state = env.agent.location
        super().__init__(self.state)
        self.map = env.things
        self.searchType = searchtype
        self.agent = env.agent



    def generateSolution(self):
        """ generate search engien based on type of the search chosen by user"""
        self.env.read_env()
        self.state = env.agent.location
        super().__init__(self.state)
        if self.searchType == 'BFS':
            print("Generating BFS Solution")
            path, explored = breadth_first_graph_search(self)
            sol = path.solution()
            self.env.set_solution(sol)
            self.env.display_explored(explored)
            self.env.display_solution()
        elif self.searchType == 'DFS':
            print("Generating DFS Solution")
            path, explored = depth_first_graph_search(self)
            sol = path.solution()
            self.env.set_solution(sol)
            self.env.display_explored(explored)
            self.env.display_solution()
        elif self.searchType == 'UCS':
            print("Generating UCS Solution")
            # path, explored = uniform_cost_search(self, True)
            path, explored = uniform_cost_search(self, False)
            sol = path.solution()
            self.env.set_solution(sol)
            self.env.display_explored(explored)
            self.env.display_solution()
        elif self.searchType == 'A*':
            print("Generating A* Solution")
            path, explored = astar_search(self)
            sol = path.solution()
            self.env.set_solution(sol)
            self.env.display_explored(explored)
            self.env.display_solution()
        else:
            print("No search type selected. Please choose valid Seach Type")
            self.env.set_solution([])
            self.env.display_explored([])
            self.env.display_solution()
            # raise 'NameError'


    def generateNextSolution(self):
        self.generateSolution()


    def find_direction(self, loc):
        x1, y1 = self.env.agent.location
        x2, y2 = loc
        if x1 == x2:
            if y1 > y2:
                return 'DOWN'
            else:
                return 'UP'
        elif y1 == y2:
            if x1 > x2:
                return 'LEFT'
            else:
                return 'RIGHT'        
        

    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list, since there are only four possible actions
        in any given state of the environment """
        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']

        possible_neighbors = self.env.things_near(state)

        for neighbour in possible_neighbors:
            thng, dstnc = neighbour
            if dstnc == 0:
                if type(thng) == Dirt:
                    if self.find_direction(thng.location) in possible_actions:
                        possible_actions.remove(self.find_direction(thng.location))
                    possible_actions.insert(0, self.find_direction(thng.location)) if self.find_direction(thng.location) is not None else None
                elif type(thng) == Wall:
                    if self.find_direction(thng.location) in possible_actions:
                        possible_actions.remove(self.find_direction(thng.location))

        # print("possible actions:", possible_actions, self.agent.location)
        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """
        new_state = list(state)
        # print(state, action)
        if action == 'UP':
            if self.env.is_inbounds((new_state[0], new_state[1] + 1)):
                new_state[1] += 1
        elif action == 'DOWN':
            if self.env.is_inbounds((new_state[0], new_state[1] - 1)):
                new_state[1] -= 1
        elif action == 'LEFT':
            if self.env.is_inbounds((new_state[0] - 1, new_state[1])):
                new_state[0] -= 1
        elif action == 'RIGHT':
            if self.env.is_inbounds((new_state[0] + 1, new_state[1])):
                new_state[0] += 1
        else:
            if self.env.dirtCount == 0:
                new_state = state
                print("No more dirt to clean. Goal state reached. ")
            else:
                print("Unknown action: ", action)
            

        # print("result(", state, action ,"):", new_state)
        return tuple(new_state)

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        # print("goal_test(", state ,"):", self.env.some_things_at(state, Dirt))
        return self.env.some_things_at(state, Dirt)


    def path_cost(self, c, state1, action, state2):
        """To be used for UCS and A* search. Returns the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. For our problem
        state is (x, y) coordinate pair. To make our problem more interesting we are going to associate
        a height to each state as z = sqrt(x*x + y*y). This effectively means our grid is a bowl shape and
        the center of the grid is the center of the bowl. So now the distance between 2 states become the
        square of Euclidean distance as distance = (x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2"""
        z1 = math.sqrt(state1[0] * state1[0] + state1[1] * state1[1])
        z2 = math.sqrt(state2[0] * state2[0] + state2[1] * state2[1])

        a = abs(state1[0] - state2[0])
        b = abs(state1[1] - state2[1])
        z = abs(int(z1 - z2))

        c += a^2 + b^2 + z^2
        # print("path_cost(", c, state1, action, state2 ,"): ", c)
        return c


    def h(self, node):
        """ to be used for A* search. Return the heuristic value for a given state. For this problem use minimum Manhattan
        distance to all the dirty rooms + absolute value of height distance as described above in path_cost() function. .
    """
        state1 = self.agent.location
        state2 = node.state
        a = abs(state1[0] - state2[0])
        b = abs(state1[1] - state2[1])
        z1 = math.sqrt(state1[0] * state1[0] + state1[1] * state1[1])
        z2 = math.sqrt(state2[0] * state2[0] + state2[1] * state2[1])
        z = abs(int(z1 - z2))
        h = a + b + z
        # print("h (heuristic): ", h)
        return h

# ______________________________________________________________________________


def agent_label(agt):
    """creates a label based on direction"""
    dir = agt.direction
    lbl = '^'
    if dir.direction == 'down':
        lbl = 'v'
    elif dir.direction == 'left':
        lbl = '<'
    elif dir.direction == 'right':
        lbl = '>'

    return lbl


def is_agent_label(lbl):
    """determines if the label is one of the labels tht agents have: ^ v < or >"""
    return lbl == '^' or lbl == 'v' or lbl == '<' or lbl == '>'


class Gui(VacuumEnvironment):
    """This is a two-dimensional GUI environment. Each location may be
    dirty, clean or can have a wall. The user can change these at each step.
    """
    xi, yi = (0, 0)

    perceptible_distance = 1

    def __init__(self, root, width, height):
        self.searchAgent = None
        print("creating xv with width ={} and height={}".format(width, height))
        super().__init__(width, height)

        self.agent = None
        self.root = root
        self.create_frames(height)
        self.create_buttons(width)
        self.create_walls()
        self.setupTestEnvironment()

    def setupTestEnvironment(self):
        """ first reset the agent"""

        if self.agent is not None:
            xi, yi = self.agent.location
            self.buttons[yi][xi].config(bg='white', text='', state='normal')
            x = self.width // 2
            y = self.height // 2
            self.agent.location = (x, y)
            self.buttons[y][x].config(bg='white', text=agent_label(self.agent), state='normal')
            self.searchType = searchTypes[0]
            self.agent.performance = 0

        """next create a random number of block walls inside the grid as well"""
        roomCount = (self.width - 1) * (self.height - 1)
        blockCount = random.choice(range(roomCount//10, roomCount//5))
        for _ in range(blockCount):
            rownum = random.choice(range(1, self.height - 1))
            colnum = random.choice(range(1, self.width - 1))
            self.buttons[rownum][colnum].config(bg='red', text='W', disabledforeground='black')

        self.create_dirts()
        self.stepCount = 0
        self.searchType = None
        self.solution = []
        self.explored = set()
        self.read_env()

    def create_frames(self, h):
        """Adds h row frames to the GUI environment."""
        self.frames = []
        for _ in range(h):
            frame = Frame(self.root, bg='blue')
            frame.pack(side='bottom')
            self.frames.append(frame)

    def create_buttons(self, w):
        """Adds w buttons to the respective row frames in the GUI."""
        self.buttons = []
        for frame in self.frames:
            button_row = []
            for _ in range(w):
                button = Button(frame, bg='white', state='normal', height=1, width=1, padx=1, pady=1)
                button.config(command=lambda btn=button: self.toggle_element(btn))
                button.pack(side='left')
                button_row.append(button)
            self.buttons.append(button_row)

    def create_walls(self):
        """Creates the outer boundary walls which do not move. Also create a random number of
        internal blocks of walls."""
        for row, button_row in enumerate(self.buttons):
            if row == 0 or row == len(self.buttons) - 1:
                for button in button_row:
                    button.config(bg='red', text='W', state='disabled', disabledforeground='black')
            else:
                button_row[0].config(bg='red', text='W', state='disabled', disabledforeground='black')
                button_row[len(button_row) - 1].config(bg='red', text='W', state='disabled', disabledforeground='black')

    def create_dirts(self):
        """ set a small random number of rooms to be dirty at random location on the grid
        This function should be called after create_walls()"""
        self.read_env()   # this is needed to make sure wall objects are created
        roomCount = (self.width-1) * (self.height -1)
        self.dirtCount = random.choice(range(5, 15))
        dirtCreated = 0
        while dirtCreated != self.dirtCount:
            rownum = random.choice(range(1, self.height-1))
            colnum = random.choice(range(1, self.width-1))
            if self.some_things_at((colnum, rownum)):
                continue
            self.buttons[rownum][colnum].config(text='D', bg='grey')
            dirtCreated += 1

    def setSearchEngine(self, choice):
        """sets the chosen search engine for solving this problem"""
        self.searchType = choice
        self.searchAgent = VacuumPlanning(self, self.searchType)
        self.searchAgent.generateSolution()
        self.done = False

    def set_solution(self, sol):
        self.solution = list(reversed(sol))
        # print("solution is {}".format(self.solution))

    def display_solution(self):
        sol_copy = self.solution.copy()
        x, y = self.agent.location
        xi, yi = self.agent.location
        while len(sol_copy) > 0:
            command = sol_copy.pop()
            if command == 'UP':
                y += 1
            elif command == 'DOWN':
                y -= 1
            elif command == 'LEFT':
                x -= 1
            elif command == 'RIGHT':
                x += 1

            if self.buttons[y][x]['text'] != 'D' and self.buttons[y][x]['text'] != 'W':
                self.buttons[y][x].config(bg='orange')
        
        lbl = agent_label(self.agent)
        self.buttons[yi][xi].config(bg='white', text=lbl, state='normal')

    def display_explored(self, explored):
        """display explored slots in a light pink color"""
        if len(self.explored) > 0:     # means we have explored list from previous search. So need to clear their visual fist
            for (x, y) in self.explored:
                if self.buttons[y][x]['text'] != 'W' and self.buttons[y][x]['text'] != 'D':
                    self.buttons[y][x].config(bg='white', text='', state='normal')

        self.explored = explored
        for (x, y) in explored:
            if self.buttons[y][x]['text'] != 'W' and self.buttons[y][x]['text'] != 'D':
                self.buttons[y][x].config(bg='pink')

    def add_agent(self, agt, loc):
        """add an agent to the GUI"""
        self.add_thing(agt, loc)
        # Place the agent at the provided location.
        lbl = agent_label(agt)
        self.buttons[loc[1]][loc[0]].config(bg='white', text=lbl, state='normal')
        self.agent = agt

    def toggle_element(self, button):
        """toggle the element type on the GUI."""
        bgcolor = button['bg']
        txt = button['text']
        if is_agent_label(txt):
            if bgcolor == 'grey':
                button.config(bg='white', state='normal')
            else:
                button.config(bg='grey')
        else:
            if bgcolor == 'red':
                button.config(bg='grey', text='D')
            elif bgcolor == 'grey':
                button.config(bg='white', text='', state='normal')
            elif bgcolor == 'white':
                button.config(bg='red', text='W')

    def execute_action(self, agent, action):
        xi, yi = agent.location
        print("agent at location (", xi, yi, ") and action ", action)
        if action == 'Suck':
            dirt_list = self.list_things_at(agent.location, Dirt)
            if dirt_list:
                dirt = dirt_list[0]
                agent.performance += 100
                self.delete_thing(dirt)
                self.buttons[yi][xi].config(bg='white', text='', state='normal')

        else:
            agent.bump = False
            if action == 'RIGHT':
                agent.direction = Direction("right")
                xf, yf = agent.direction.move_forward(agent.location)
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                # self.buttons[yf][xf].config(text=agent_label(agent))
            elif action == 'LEFT':
                agent.direction = Direction("left")
                xf, yf = agent.direction.move_forward(agent.location)
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                # self.buttons[yf][xf].config(text=agent_label(agent))
            elif action == 'UP':
                agent.direction = Direction("up")
                xf, yf = agent.direction.move_forward(agent.location)
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                # self.buttons[yf][xf].config(text=agent_label(agent))
            elif action == 'DOWN':
                agent.direction = Direction("down")
                xf, yf = agent.direction.move_forward(agent.location)
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                # self.buttons[yf][xf].config(text=agent_label(agent))

        if action != 'NoOp':
            agent.performance -= 1

        self.buttons[yi][xi].config(text='')
        xf, yf = agent.location
        self.buttons[yf][xf].config(text=agent_label(agent))
        # print("agent moved to location (", agent.location[0], agent.location[1], ") and direction is ", agent.direction.direction)
        """Determines the action the agent performs."""
        # print("execute_actin: to be done by students")

        NumSteps_label.config(text=str(self.stepCount))
        TotalCost_label.config(text=str(self.agent.performance))

    def read_env(self):
        """read_env: This sets proper wall or Dirt status based on bg color"""
        """Reads the current state of the GUI environment."""
        self.dirtCount = 0
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)):  # and (i, j) != agt_loc:
                        for thing in self.list_things_at((i, j)):
                            if not isinstance(thing, Agent):
                                self.delete_thing(thing)
                    if btn['bg'] == 'grey':  # adding dirt
                        self.add_thing(Dirt(), (i, j))
                        self.dirtCount += 1
                    elif btn['bg'] == 'red':  # adding wall
                        self.add_thing(Wall(), (i, j))

    def update_env(self):
        """Updates the GUI environment according to the current state."""
        self.read_env()
        self.step()
        self.stepCount += 1

    def step(self):
        """updates the environment one step. Currently it is associated with one click of 'Step' button.
        """
        if env.dirtCount == 0:
            print("Everything is clean. DONE!")
            env.set_solution([])
            env.display_explored([])
            env.display_solution()
            self.done = True
            return

        if len(self.solution) == 0:
            self.execute_action(self.agent, 'Suck')
            self.read_env()
            if env.dirtCount > 0 and self.searchAgent is not None:
                self.searchAgent.generateNextSolution()
                self.running = False
        else:
            move = self.solution.pop()
            self.execute_action(self.agent, move)


    def run(self, steps=1000, delay=0.2):
        """Run the Environment for given number of time steps,"""
        i = 1
        while i <= steps and not self.done:
            i += 1
            self.update_env()
            time.sleep(delay)

        if (i == steps):
            print("Done running for ", i, " steps")
        # print("Done running for ", i, " steps")

    def reset_env(self):
        """Resets the GUI and agents environment to the initial clear state."""
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)):
                        for thing in self.list_things_at((i, j)):
                            self.delete_thing(thing)
                    btn.config(bg='white', text='', state='normal')

        self.agent = None
        self.dirtCount = 0
        self.stepCount = 0
        self.solution = []
        self.searchAgent = None
        self.running = False
        self.done = False
        NumSteps_label.config(text=str(0))
        TotalCost_label.config(text=str(0))
        searchTypeStr.set(searchTypes[0])
        
        self.setupTestEnvironment()

        theAgent = XYSearchAgent(program=XYSearchAgentProgram, loc=(hig//2, wid//2))
        x, y = theAgent.location
        self.add_agent(theAgent, (y, x))





"""
Our search Agents ignore ignore environment percepts for planning. The planning is done based ons static
 data from environment at the beginning. The environment if fully observable
 """
def XYSearchAgentProgram(percept):
    pass


class XYSearchAgent(Agent):
    """The modified SimpleRuleAgent for the GUI environment."""

    def __init__(self, program, loc):
        super().__init__(program)
        self.location = loc
        self.direction = Direction("up")
        self.searchType = searchTypes[0]
        self.stepCount = 0
        self.holding = []


if __name__ == "__main__":
    win = Tk()
    win.title("Searching Cleaning Robot")
    # win.geometry("800x750+50+50")
    win.resizable(True, True)
    frame = Frame(win, bg='black')
    frame.pack(side='bottom')
    topframe = Frame(win, bg='black')
    topframe.pack(side='top')

    wid = 10
    if len(sys.argv) > 1:
        wid = int(sys.argv[1])

    hig = 10
    if len(sys.argv) > 2:
        hig = int(sys.argv[2])

    env = Gui(win, wid, hig)

    theAgent = XYSearchAgent(program=XYSearchAgentProgram, loc=(hig//2, wid//2))
    x, y = theAgent.location
    env.add_agent(theAgent, (y, x))

    NumSteps_label = Label(topframe, text='NumSteps: 0', bg='green', fg='white', bd=2, padx=2, pady=2)
    NumSteps_label.pack(side='left')
    TotalCost_label = Label(topframe, text='TotalCost: 0', bg='blue', fg='white', padx=2, pady=2)
    TotalCost_label.pack(side='right')
    reset_button = Button(frame, text='Reset', height=2, width=5, padx=2, pady=2)
    reset_button.pack(side='left')
    next_button = Button(frame, text='Next', height=2, width=5, padx=2, pady=2)
    next_button.pack(side='left')
    run_button = Button(frame, text='Run', height=2, width=5, padx=2, pady=2)
    run_button.pack(side='left')

    next_button.config(command=env.update_env)
    reset_button.config(command=env.reset_env)
    run_button.config(command=env.run)

    searchTypeStr = StringVar(win)
    searchTypeStr.set(searchTypes[0])
    searchTypeStr_dropdown = OptionMenu(frame, searchTypeStr, *searchTypes, command=env.setSearchEngine)
    searchTypeStr_dropdown.pack(side='left')

    win.mainloop()
