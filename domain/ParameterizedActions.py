import Domain.StaticConstants as Constants

class ParameterizedActions:
    def __init__(self, type, n):
        self.type = type
        self.n = n

    def applicableActions(self, s):
        pass

    def returnType(self):
        self.type

class Sample(ParameterizedActions):
    def applicableActions(self, s):
        actions = []
        agentx = s.agent.x
        agenty = s.agent.y
        rocks = s.rocks
        for i, rock in rocks.items():
            if rock.x == agentx and rock.y == agenty and not rock.collected:
                actions.append(Constants.ACTION_SAMPLE)
        return actions

class Check(ParameterizedActions):
    def applicableActions(self, s):
        actions = []
        rocks = s.rocks
        for i, rock in rocks.items():
            if not rock.collected:
                actions.append(Constants.ACTION_CHECK+"_"+str(i))
        return actions

class Move(ParameterizedActions):
    def applicableActions(self, s):
        actions = []
        agentx = s.agent.x
        agenty = s.agent.y

        if agenty + 1 < self.n:
            actions.append(Constants.ACTION_MOVE+"_North")
        if agenty - 1 >= 0:
            actions.append(Constants.ACTION_MOVE+"_South")
        if agentx + 1 <= self.n:
            actions.append(Constants.ACTION_MOVE+"_East")
        if agentx - 1 >= 0 :
            actions.append(Constants.ACTION_MOVE+"_West")

        return actions
