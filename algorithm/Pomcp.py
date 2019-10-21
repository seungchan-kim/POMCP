import math
import numpy as np
import domain.StaticConstants as Constants
import copy
from pdb import set_trace as bp

class Pomcp:
    def __init__(self, debug, domain, pomcpParameters, pomcpRn):
        self.PARAMETERS = pomcpParameters
        self.RANDOM = pomcpRn
        self.DOMAIN = domain
        self.POMCP_DEPTH = 0
        self.MAX_DEPTH_REACHED = 0
        self.DEBUG = debug

    def initializePomcp(self, initialState, beliefEstimate):
        root = VNode(None, None)
        root.initializeVNode(initialState, self.DOMAIN)
        root.beliefEstimate = beliefEstimate
        return root

    def beliefUpdate(self, root, action, observation):
        qNode = root.children[action]
        vNode = qNode.children.get(observation)

        if vNode == None:
            qNode.children[observation] = VNode(action, observation)
            vNode = qNode.children[observation]

        if len(vNode.beliefEstimate):
            particle = self.RANDOM.choice(vNode.beliefEstimate)
        else:
            return "particle Depletion"

        if self.PARAMETERS.pomcpReinvigorateSamples > 0:
            self.particleReinvigoration(root, vNode, action, observation)

        return self.initializePomcp(particle, vNode.beliefEstimate)


    def particleReinvigoration(self, root, vNode, action, observation):
        added = 0
        a = Constants.parseAction(action)
        if a[0] == Constants.ACTION_CHECK:
            while (added < self.PARAMETERS.pomcpReinvigorateSamples):
                ## we will create transform

                # sample a state particle from root.beliefEstimate
                state = self.RANDOM.choice(root.beliefEstimate)
                #outcome = self.sampleGenerativeModel(state, action)
                next_state, r, term, obs = self.sampleGenerativeModel(state, action)

                #use the next_state to create
                rockstate = copy.deepcopy(next_state)
                rockIndex = self.RANDOM.randint(0,len(rockstate.rocks)-1) #randomly choosing ith rock
                #make perturbations by swapping the status of the ith rock
                rockstate.rocks[rockIndex].good = not rockstate.rocks[rockIndex].good
                transform = rockstate #transformed rockstate

                #make new observations using the transformed state (transform) and action
                newObservation = self.DOMAIN.Model.ObservationFunction.sample(transform, action)
                if observation == newObservation: #compare the real observation and new observation
                    vNode.beliefEstimate.append(transform) #if yes, add to the beliefEstimate of vNode
                    added += 1

    
    def selectAction(self, root):
        for i in range(self.PARAMETERS.maxSamples):
            self.POMCP_DEPTH = 0
            particle = self.RANDOM.choice(root.beliefEstimate)
            self.simulateV(root, particle)

        for action in root.children:
            q = root.children[action]
            if q.children:
                for o in q.children:
                    v = q.children[o]
                    # if self.DEBUG > 2:
                    #     print(action, o, len(v.beliefEstimate))

        return self.greedyUCB(root, False)

    def simulateV(self, vNode, state):
        if self.POMCP_DEPTH >= self.PARAMETERS.pomcpDepth:
            return 0.0

        action = self.greedyUCB(vNode, True)
        if self.POMCP_DEPTH == 1:
            vNode.beliefEstimate.append(state)

        qNode = vNode.children[action]
        qValue = self.simulateQ(qNode, state, action)
        vNode.rewardEstimate.append(qValue)
        return qValue

    def simulateQ(self, qNode, state, action):
        [s_, r, terminated, o] = self.sampleGenerativeModel(state, action)
        #print(state.agent.x, state.agent.y, action, s_.agent.x, s_.agent.y,o,r)

        vNode = qNode.children.get(o)
        if vNode == None:
            qNode.children[o] = VNode(action, o)
            vNode = qNode.children[o]

        if not terminated and not vNode.children and len(qNode.rewardEstimate) >= 1:
            qNode.children[o].initializeVNode(s_, self.DOMAIN)

        delayedReward = 0
        if not terminated:
            self.POMCP_DEPTH += 1
            if self.POMCP_DEPTH > self.MAX_DEPTH_REACHED: self.MAX_DEPTH_REACHED = self.POMCP_DEPTH

            if vNode.children: #if visited before
                delayedReward = self.simulateV(vNode, s_)

            else:
                delayedReward = self.rollout(s_, 0, self.PARAMETERS.pomcpDiscount, False)
            self.POMCP_DEPTH -= 1
        rewardTotal = round(r + self.PARAMETERS.pomcpDiscount * delayedReward, 3)
        qNode.rewardEstimate.append(rewardTotal)
        return rewardTotal

    def rollout(self, state, depth, discount, terminated):
        if (depth > self.PARAMETERS.pomcpDepth or terminated):
            return 0
        action = self.DOMAIN.selectRandomAction(state)
        [s_, r, terminated, o] = self.sampleGenerativeModel(state, action)
        #reward += r * discount
        depth += 1
        return r + discount * self.rollout(s_, depth, discount, terminated) #fix rollout

    def sampleGenerativeModel(self, state, action):
        s_ = self.DOMAIN.Model.TransitionFunction.sample(state, action)
        r = self.DOMAIN.Model.RewardFunction.reward(state, action, s_)
        t = self.DOMAIN.Model.TerminationFunction.isTerminal(s_)
        o = self.DOMAIN.Model.ObservationFunction.sample(s_, action)
        return [s_, r, t, o]

    def greedyUCB(self, vNode, ucb):
        qValues = []
        actions = []
        #maxQ = -float("inf")
        action = None
        for qn in vNode.children.values():
            cumulativeReward = sum(qn.rewardEstimate)
            qvalue = cumulativeReward / len(qn.rewardEstimate) if len(qn.rewardEstimate) else 0

            if ucb:
                if len(qn.rewardEstimate):
                    qvalue += self.PARAMETERS.pomcpExploration * \
                              math.sqrt(math.log(len(vNode.rewardEstimate)) / len(qn.rewardEstimate))
                else:
                    qvalue = float('inf')

            #if qvalue > maxQ:
            #    maxQ = qvalue
            #   action = qn.nextAction



            qValues.append(qvalue)
            actions.append(qn.nextAction)

        if not ucb and self.DEBUG > 2:
            for i in range(0,len(actions)):
                print(actions[i], ":", qValues[i])
        winner = np.argwhere(qValues == np.amax(qValues)).flatten().tolist()
        win = self.RANDOM.choice(winner)
        action = actions[win]
        return action


class VNode:

    def __init__(self, action, observation):
        self.action = action
        self.observation = observation
        self.rewardEstimate = []
        self.beliefEstimate = []
        self.children = {}

    
    def initializeVNode(self, state, domain):
        for action in domain.applicableActions(state):
            qNode = QNode(action)
            self.children[action] = qNode

class QNode:
    def __init__(self, action):
        self.nextAction = action
        self.rewardEstimate = []
        self.children = {}

