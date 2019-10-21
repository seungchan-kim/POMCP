class Environment():
    def __init__(self, domain, s):
        self.domain = domain
        self.s = s

class SimulatedEnvironment(Environment):
    def executeAction(self, a):
        s_ = self.domain.Model.TransitionFunction.sample(self.s, a)
        r = self.domain.Model.RewardFunction.reward(self.s, a, s_)
        t = self.domain.Model.TerminationFunction.isTerminal(s_)
        o = self.domain.Model.ObservationFunction.sample(s_,a)
        self.s = s_
        return [s_, o, a, r, t]

    def simulator(self, n, k, s):
        for y in range(n-1,-1,-1):
            line = ""
            for x in range(0,n):
                char = self.checkRock(k,s,x,y)
                if s.agent.x == x and s.agent.y == y:
                    char = "A"
                line += char
            print(line)


    def checkRock(self, k, s, x, y):
        for k in range(1, k + 1):
            if s.rocks[k].x == x and s.rocks[k].y == y:
                if s.rocks[k].collected:
                    if s.rocks[k].good:
                        return "G"
                    else:
                        return "B"
                else:
                    return str(k)
        return "_"
