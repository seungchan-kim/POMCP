import numpy as np
from Domain.State import State, Agent, Rock
from Domain import ParameterizedActions as Actions
from Domain import StaticConstants as Constants
import Domain.Model as Model
import copy
from pdb import set_trace as bp

class Domain:
    ActionTypes = []
    Model = []

    def __init__(self, n, k, rand):
        self.n = n
        self.k = k
        self.gamma = 0.99
        self.RANDOM = rand

    def makeInitialState(self):
        agent = Agent.agent(self.RANDOM.randint(0,self.n-1), self.RANDOM.randint(0,self.n-1))
        rockEmpty = np.zeros((self.n, self.n))
        rocks = {}
        count = 0
        while count < self.k:
            rx = self.RANDOM.randint(0,self.n-1)
            ry = self.RANDOM.randint(0,self.n-1)
            rock = Rock.rock(rx, ry, self.RANDOM.choice([True,False]), False)
            if rockEmpty[rx][ry] == 0:
                rocks[count+1] = rock
                rockEmpty[rx][ry] = 1
                count += 1
        return State.state(agent, rocks)

    def applicableActions(self, s):
        applicableActions = []
        for action in self.ActionTypes:
            applicableActions += action.applicableActions(s)
        return applicableActions


    def generateDomain(self, s):
        self.ActionTypes.append(Actions.Move(Constants.ACTION_MOVE,self.n))
        self.ActionTypes.append(Actions.Sample(Constants.ACTION_SAMPLE,self.n))
        self.ActionTypes.append(Actions.Check(Constants.ACTION_CHECK,self.n))
        self.Model = Model.Model(self.n,self.k,self.RANDOM)


    def selectRandomAction(self, state):
        applicableActions = self.applicableActions(state)
        return self.RANDOM.choice(applicableActions)
