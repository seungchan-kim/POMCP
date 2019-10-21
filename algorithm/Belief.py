import Domain.State.State as State
import Domain.State.Rock as Rock
import copy

class belief:
    def __init__(self):
        pass

    def pomcpSample(self, s, numSamples, rand):
        beliefEstimate = []
        for i in range(numSamples):
            beliefEstimate.append(self.sampleState(s, rand))
        return beliefEstimate

    def sampleState(self, s, rand):
        newRocks = {}
        for i, rock in s.rocks.items():
            newRock = Rock.rock(rock.x, rock.y, rand.choice([True, False]), False)
            newRocks[i] = newRock
        newState = State.state(s.agent, newRocks)
        return newState
