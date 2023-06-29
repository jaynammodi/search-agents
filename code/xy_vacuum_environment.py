import os.path
from tkinter import *
from agents import *
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def agent_label(agt):
    """creates a label based on direction"""
    dir = agt.direction
    lbl = '^'
    if dir.direction == Direction.U:
        lbl = 'v'
    elif dir.direction == Direction.L:
        lbl = '<'
    elif dir.direction == Direction.R:
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
    xy = {}
    perceptible_distance = 1
    agentTypes = ['ReflexAgent', 'RuleAgent', "NoAgent"]

    def __init__(self, root, width=7, height=7):
        print("creating xv with width ={} and height={}".format( width, height))
        super().__init__(width, height)

        self.root = root
        self.create_frames(height)
        self.create_buttons(width)
        self.create_walls()
        self.agentType = self.agentTypes[0]
        self.secondAgentType = self.agentTypes[0]   # no second agent at start.

    def create_frames(self, h):
        """Adds frames to the GUI environment."""
        self.frames = []
        for _ in range(h):
            frame = Frame(self.root, bg='blue')
            frame.pack(side='bottom')
            self.frames.append(frame)

    def create_buttons(self, w):
        """Adds buttons to the respective frames in the GUI."""
        self.buttons = []
        for frame in self.frames:
            button_row = []
            for _ in range(w):
                button = Button(frame, bg='white', height=2, width=3, padx=2, pady=2)
                button.config(command=lambda btn=button: self.toggle_element(btn))
                button.pack(side='left')
                button_row.append(button)
            self.buttons.append(button_row)

    def create_walls(self):
        """Creates the outer boundary walls which do not move."""
        for row, button_row in enumerate(self.buttons):
            if row == 0 or row == len(self.buttons) - 1:
                for button in button_row:
                    button.config(bg='red', text='W', state='disabled', disabledforeground='black')
            else:
                button_row[0].config(bg='red',text='W', state='disabled', disabledforeground='black')
                button_row[len(button_row) - 1].config(bg='red', text='W', state='disabled', disabledforeground='black')

    def add_agent(self, agt, xyloc):
        """add an agent to the GUI"""
        self.add_thing(agt, xyloc)
        # Place the agent in the centre of the grid.
        lbl = agent_label(agt)
        self.xy[agt] = xyloc
        self.buttons[xyloc[1]][xyloc[0]].config(bg='white', text=lbl)

    def toggle_element(self, button):
        """toggle the element type on the GUI."""
        bgcolor = button['bg']
        txt = button['text']
        if is_agent_label(txt):
            if bgcolor == 'grey':
                button.config(bg='white')
            else:
                button.config(bg='grey')
        else:
            if bgcolor == 'red':
                button.config(bg='grey', text='D')
                self.add_thing(Dirt(), (self.xi, self.yi))
            elif bgcolor == 'grey':
                button.config(bg='white', text='')
            elif bgcolor == 'white':
                button.config(bg='red', text='W')

    def execute_action(self, agent, action):
        """Determines the action the agent performs."""
        # xi, yi = (self.xi, self.yi)
        xi, yi = agent.location
        print("agent at location (", xi, yi, ") and action ", action)
        if action == 'Suck':
            dirt_list = self.list_things_at(agent.location, Dirt)
            if dirt_list:
                dirt = dirt_list[0]
                agent.performance += 100
                self.delete_thing(dirt)
                self.buttons[yi][xi].config(bg='white')

        else:
            agent.bump = False
            if action == 'TurnRight':
                agent.direction += Direction.R
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'TurnLeft':
                agent.direction += Direction.L
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'Forward':
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                if not agent.bump:
                    self.buttons[yi][xi].config(text='')
                    xf, yf = agent.location
                    # print("agent moved to location (", xf, yf, ")")
                    self.buttons[yf][xf].config(text=agent_label(agent))

        if action != 'NoOp':
            agent.performance -= 1

        performance_label.config(text=str(agent.performance))

    def read_env(self, agt):
        """read_env: This sets proper wall or Dirt status based on bg color"""
        # agt_loc = self.agents[0].location
        agt_loc = agt.location

        """Reads the current state of the GUI environment."""
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)) and (i, j) != agt_loc:
                        for thing in self.list_things_at((i, j)):
                            if not isinstance(thing, Agent):
                                self.delete_thing(thing)
                    if btn['bg'] == 'grey': # adding dirt
                        self.add_thing(Dirt(), (i, j))
                    elif btn['bg'] == 'red': # adding wall
                        self.add_thing(Wall(), (i, j))

    def update_env(self):
        # print(self.xy)
        """Updates the GUI environment according to the current state."""
        for agt in self.agents:
            self.read_env(agt)
        # agt = self.agents[0]
            # print(self.xy[agt])
            previous_agent_location = agt.location
            self.xy[agt] = previous_agent_location
            # self.xi, self.yi = previous_agent_location
        self.step()
        print("--------------------")



    def toggle_agentType(self):
        """toggles the type of the agent. Choices are 'Reflex' and 'RuleBased'."""
        if env.agentType == env.agentTypes[0]:
            env.agentType = env.agentTypes[1]
        else:
            env.agentType = env.agentTypes[0]

        print(", new agentType = ", env.agentType)
        agentType_button.config(text=env.agentType)

        self.reset_env()

    # def toggle_secondAgentType(self):
    #     """toggles the type of the agent. Choices are 'Reflex' and 'RuleBased'."""
    #     if env.secondAgentType == env.agentTypes[0]:
    #         env.secondAgentType = env.agentTypes[1]
    #     else:
    #         env.secondAgentType = env.agentTypes[0]

    #     print(", new secondAgentType = ", env.secondAgentType)
    #     agentType_button.config(text=env.secondAgentType)

    #     self.reset_env()

    def reset_env(self):
        # print(self.agentType, "agent1")
        # print(self.secondAgentType, "agent2")
        self.xy = {}
        self.agents = []
        """Resets the GUI environment to the initial clear state."""
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)) :
                        for thing in self.list_things_at((i, j)):
                            if not isinstance(thing, Agent):
                                self.delete_thing(thing)
                    btn.config(bg='white', text='', state='normal')

        bound1 = (0,0)
        bound2 = (0,0)
        if self.secondAgentType != "NoAgent":
            bound1 = (0, hig//2 - 1)
            bound2 = (hig//2, hig - 1)

        theAgent = XYReflexAgent(program=lambda agent:XYReflexAgentProgram(self.percept(theAgent), theAgent.location, theAgent.direction, bound_h=bound1))
        if self.agentType == 'RuleAgent':
            # theAgent = RuleBasedAgent(program=XYRuleBasedAgentProgram)
            theAgent = RuleBasedAgent(program=lambda agent:XYRuleBasedAgentProgram(self.percept(theAgent), self.list_things_at, theAgent.location, theAgent.direction, bound_h=bound1))


        x1, y1 = ((wid-1) // 2, (hig) // 2)


        if self.secondAgentType != 'NoAgent':
            x1, y1 = ((wid-1) // 2, (hig) // 4)
            theSecondAgent = XYReflexAgent(program=lambda agent:XYReflexAgentProgram(self.percept(theSecondAgent), theSecondAgent.location, theSecondAgent.direction, bound_h=bound2))
            # theSecondAgent = XYReflexAgent(program=XYReflexAgentProgram)
            if self.secondAgentType == 'RuleAgent':
                # theSecondAgent = RuleBasedAgent(program=XYRuleBasedAgentProgram)
                theSecondAgent = RuleBasedAgent(program=lambda agent:XYRuleBasedAgentProgram(self.percept(theSecondAgent), self.list_things_at, theSecondAgent.location, theSecondAgent.direction, bound_h=bound2))

            x2, y2 = ((wid-1) // 2, 3 * (hig-1) // 4)
            # add an agent at location 3, 3.
            self.add_thing(theSecondAgent, location=(x2, y2))
            self.buttons[y2][x2].config(text=agent_label(theSecondAgent))
            
            self.xy[theSecondAgent] = theSecondAgent.location


        self.add_thing(theAgent, location=(x1, y1))
        self.buttons[y1][x1].config(text=agent_label(theAgent))

        self.xy[theAgent] = theAgent.location
        # print(self.agents)
        # print("xy", self.xy)
        # print("agents", self.agents)
        # print("agent1", self.agentType)
        # print("agent2", self.secondAgentType)

    def second_agent(self):
        """Implement this: Click call back for second Agent. It rotates among possible options"""
        """toggles the type of the agent. Choices are 'Reflex' and 'RuleBased'."""
        if env.secondAgentType == env.agentTypes[0]:
            env.secondAgentType = env.agentTypes[1]
        elif env.secondAgentType == env.agentTypes[1]:
            env.secondAgentType = env.agentTypes[2]
        else:
            env.secondAgentType = env.agentTypes[0]

        print(", new secondAgentType = ", env.secondAgentType)
        secondAgent_button.config(text=env.secondAgentType)

        self.reset_env()
        pass

    def run_till_dirty(self):
        self.read_env(self.agents[0])
        print("Running til dirty")
        """Run the Environment for minimum steps while dirt blocks exist in environment"""
        count = 0
        while count <= 1000:
            if self.is_dirty():
                print(self.is_dirty())
                self.step()
                count += 1
            else:
                print(" > Steps taken = ", count)
                return
            
        print(" > Steps taken = ", count)
        print(" > Maximum Steps Reached, unable to clean.")

#implement this. Rule is as follows: At each location, agent checks all the neighboring location: If a "Dirty"
# location found, agent goes to that location, otherwise follow similar rules as the XYReflexAgentProgram bellow.
# def XYRuleBasedAgentProgram(percept):
#     status, bump = percept
#     if status == 'Dirty':
#         return 'Suck'

#     if bump == 'Bump':
#         value = random.choice((1, 2))
#     else:
#         value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward

#     if value == 1:
#         return 'TurnRight'
#     elif value == 2:
#         return 'TurnLeft'
#     else:
#         return 'Forward'

def XYRuleBasedAgentProgram(percept, listAt, loc, dir, bound_h = (0,0)):

    # print("Rule Based", percept)
    status, bump = percept

    if status == 'Dirty':
        return 'Suck'
    
    n_per = {
    }

    for x in [Direction.R, Direction.L, "backwards", "forwards"]:
        
        new_dir = dir if x == "forwards" else dir + Direction.L + Direction.L if x == "backwards" else dir + x

        new_loc = new_dir.move_forward(loc)
        if bound_h != (0,0):
            f = listAt(new_loc) if new_loc[1] in range(bound_h[0], bound_h[1]+1) else []
        else:
            f = listAt(new_loc)
        # print(x, f)
        try:
            n_per[x] = "Wall" if type(f[0]) == Wall else "Dirt" if type(f[0]) == Dirt else "Empty"
        except Exception as e:
            n_per[x] = "Empty"

    # print(n_per)
    # print(status, bump)
    if bound_h != (0,0):
        if dir.move_forward(loc)[1] < bound_h[0] or dir.move_forward(loc)[1] > bound_h[1]:
            bump = 'Bump'

    if n_per["forwards"] == "Dirt" and bump != 'Bump':
        return 'Forward'
    elif n_per["right"] == "Dirt":
        return 'TurnRight'
    elif n_per["left"] == "Dirt":
        return 'TurnLeft'
    elif n_per["backwards"] == "Dirt":
        return 'TurnLeft'
    
    if bump == 'Bump':
        value = random.choice((1, 2))
        if value == 1:
            return 'TurnRight'
        elif value == 2:
            return 'TurnLeft'

    value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
    # value = random.choice((3, 4))  # 1-right, 2-left, others-forward

    if value == 1:
        return 'TurnRight'
    elif value == 2:
        return 'TurnLeft'
    else:
        return 'Forward'



#Implement this: This will be similar to the ReflectAgent bellow.
class RuleBasedAgent(Agent):
    """Implement this: The modified SimpleRuleAgent for the GUI environment."""
    def __init__(self, program):
        super().__init__(program)
        self.location = (3, 3)
        self.direction = Direction("up")
        self.type = env.agentTypes[1]

def XYReflexAgentProgram(percept, loc=(), dir = None, bound_h = (0,0)):
    """The modified SimpleReflexAgentProgram for the GUI environment."""
    status, bump = percept
    if status == 'Dirty':
        return 'Suck'

    if bound_h != (0,0):
        if dir.move_forward(loc)[1] < bound_h[0] or dir.move_forward(loc)[1] > bound_h[1]:
            bump = 'Bump'
    if bump == 'Bump':
        value = random.choice((1, 2))
    else:
        value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
        # value = random.choice((3, 4))  # 1-right, 2-left, others-forward

    if value == 1:
        return 'TurnRight'
    elif value == 2:
        return 'TurnLeft'
    else:
        return 'Forward'

class XYReflexAgent(Agent):
    """The modified SimpleReflexAgent for the GUI environment."""
    def __init__(self, program):
        super().__init__(program)
        self.location = (1, 2)
        self.direction = Direction("up")
        self.type = env.agentTypes[0]


#
#
if __name__ == "__main__":
    win = Tk()
    win.title("Vacuum Robot Environment")
    # win.geometry("500x600")
    # win.resizable(True, True)
    frame = Frame(win, bg='black')
    frame.pack(side='bottom')

    wid = 7
    if sys.argv[1]:
        wid = int(sys.argv[1])

    hig = 7
    if sys.argv[2]:
        hig = int(sys.argv[2])

    env = Gui(win, wid, hig)

    bound1 = (0,0)
    bound2 = (0,0)
    if env.secondAgentType != "NoAgent":
        bound1 = (0, hig//2 - 1)
        bound2 = (hig//2, hig - 1)
        agt2 = XYReflexAgent(program=lambda agent:XYReflexAgentProgram(env.percept(agt2), agt2.location, agt2.direction, bound_h=bound2))
        env.add_agent(agt2, ((wid-1)// 2, 3 * (hig-1) // 4))

    agt = XYReflexAgent(program=lambda agent:XYReflexAgentProgram(env.percept(agt), agt.location, agt.direction, bound_h=bound1))
    env.add_agent(agt, ((wid-1) // 2, (hig) // 4))


    secondAgent_button = Button(frame, text=env.agentTypes[0], height=2, width=8, padx=2, pady=2)
    secondAgent_button.pack(side='left')
    agentType_button = Button(frame, text=env.agentTypes[0], height=2, width=8, padx=2, pady=2)
    agentType_button.pack(side='left')
    performance_label = Label(win, text='0', height=1, width = 3, padx=2, pady=2)
    performance_label.pack(side='top')
    reset_button = Button(frame, text='Reset', height=2, width=5, padx=2, pady=2)
    reset_button.pack(side='left')
    next_button = Button(frame, text='Next', height=2, width=5, padx=2, pady=2)
    next_button.pack(side='left')
    run_button = Button(frame, text='Run', height=2, width=5, padx=2, pady=2)
    run_button.pack(side='left')

    next_button.config(command=env.update_env)
    agentType_button.config(command=env.toggle_agentType)
    reset_button.config(command=env.reset_env)
    run_button.config(command=env.run_till_dirty)
    secondAgent_button.config(command=env.second_agent)


    win.mainloop()
