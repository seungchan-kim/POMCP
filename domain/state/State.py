class state:
    def __init__(self, agent, rocks):
        self.agent = agent
        self.rocks = rocks

    def findRock(self, x, y):
        rocks = self.rocks
        index = -1
        for i, rock in rocks.items(): # rocks is a collection (hash table) of rock
            if rock.x == x and rock.y == y:
                index = i
        return index

    def __str__(self):
        #agent = "AGENT:(" + str(self.agent.x) + "," + str(self.agent.y) + ")"
        rocks = "ROCKS:"
        for i in self.rocks:
            rocks += "(" + str(self.rocks[i].x) + "," + str(self.rocks[i].y)
            if self.rocks[i].good:
                rocks += ",T)"
            else:
                rocks += ",F)"
        #return agent + rocks
        return rocks
