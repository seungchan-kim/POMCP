import domain.StaticConstants as Constants
import domain.state.State as st
import domain.state.Agent as ag
import copy
import math


class Model:
    def __init__(self,n,k,random):
        self.n = n
        self.k = k
        self.RewardFunction = self.RewardFunction(self.n, self.k)
        self.TerminationFunction = self.TerminationFunction(self.n)
        self.TransitionFunction = self.TransitionFunction(self.n, self.k)
        self.ObservationFunction = self.ObservationFunction(random)

    class RewardFunction:
        def __init__(self,n,k):
            self.n = n
            self.k = k


        def reward(self, s, a, s_):
            a = Constants.parseAction(a)
            if a[0] == Constants.ACTION_MOVE and a[1] == "East" and s.agent.x+1 == self.n:
                return 10

            if a[0] == Constants.ACTION_MOVE and a[1] == "North" and s.agent.y + 1 >= self.n:
                return -100

            if a[0] == Constants.ACTION_MOVE and a[1] == "South" and s.agent.y - 1 < 0:
                return -100

            if a[0] == Constants.ACTION_MOVE and a[1] == "West" and s.agent.x - 1 < 0:
                return -100

            if a[0] == Constants.ACTION_SAMPLE:
                index = s.findRock(s.agent.x, s.agent.y)


                if index >= 0:
                    rock = s.rocks[index]
                    if not rock.collected:
                        if rock.good:
                            return 10
                        else:
                            return -10
                    else:
                        return -100
            return 0

    class TerminationFunction:
        def __init__(self, n):
            self.n = n

        def isTerminal(self, s):
            if s.agent.x >= self.n:
                return True
            return False

    class TransitionFunction:
        def __init__(self, n, k):
            self.n = n
            self.k = k

        def sample(self, s, a, deterministic=True):
            s1 = self.stateTransitions(s,a)
            return s1
        
        def stateTransitions(self, s, a):
            a = Constants.parseAction(a)
            s1 = copy.deepcopy(s)

            north = s.agent.y+1 if s.agent.y+1 < self.n else s.agent.y
            south = s.agent.y-1 if s.agent.y-1 >= 0 else s.agent.y
            east = s.agent.x+1 if s.agent.x+1 <= self.n else s.agent.x
            west = s.agent.x-1 if s.agent.x-1 >= 0 else s.agent.x

            if a[0] == Constants.ACTION_MOVE:
                if a[1] == "North":
                    s1 = st.state(ag.agent(s.agent.x, north), s.rocks)
                elif a[1] == "South":
                    s1 = st.state(ag.agent(s.agent.x, south), s.rocks)
                elif a[1] == "East":
                    s1 = st.state(ag.agent(east, s.agent.y), s.rocks)
                elif a[1] == "West":
                    s1 = st.state(ag.agent(west, s.agent.y), s.rocks)

            elif a[0] == Constants.ACTION_SAMPLE:
                index = s.findRock(s.agent.x, s.agent.y)
                rock = s.rocks[index]
                if not rock.collected:
                    s1.rocks[index].collected = True

            return s1

    class ObservationFunction:
        halfEfficiencyDistance = 20.0

        def __init__(self, random):
            self.rand = random

        def probability(self, o, s_, a):
            observationTransition = self.observationTransition(s_,a)
            if o not in observationTransition:
                return 0
            return observationTransition[o]

        def observationTransition(self, s_, action):
            observation_probabilities = {}
            a = Constants.parseAction(action)
            if a[0] == Constants.ACTION_CHECK:
                i = int(a[1])
                rock = s_.rocks[i]
                agent = s_.agent
                distance = self.euclideanDistance(rock,agent)
                efficiency = (1.0+math.pow(2,-distance/self.halfEfficiencyDistance))*0.5
                #efficiency = 1.0

                if rock.good:
                    observation_probabilities[str(i)+'_good'] = efficiency
                    observation_probabilities[str(i)+'_bad'] = 1.0 - efficiency
                else:
                    observation_probabilities[str(i)+'_bad'] = efficiency
                    observation_probabilities[str(i)+'_good'] = 1.0 - efficiency
            else:
                observation_probabilities[Constants.OBS_NULL] = 1.0
            return observation_probabilities

        def sample(self, s_, a):
            observationTransition = self.observationTransition(s_,a)
            curSum = 0.
            roll = self.rand.random()
            for o in observationTransition:
                curSum += observationTransition[o]
                if (roll <= curSum):
                    return o


        def euclideanDistance(self, rock, agent):
            return math.sqrt(math.pow(abs(rock.x - agent.x),2)
                             + math.pow(abs(rock.y - agent.y),2))
