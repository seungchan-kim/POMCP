import domain.state as State
import domain.Domain as Domain
import algorithm.Belief as Belief
import SimulatedEnvironment as Environment
import algorithm.Pomcp as Pomcp
import numpy as np
from pdb import set_trace as bp

def executeSearchWorld(debug, rand, n, k, pomcpParameters):
    if n == 0 and k == 0:
        domain = Domain.Domain(n,k,rand)
        initialState = domain.makeInitialState()
    elif n == 7 and k == 8:
        domain = Domain.Domain(n,k,rand)
        initialState = domain.makeInitialState()
        initialState.agent.x, initialState.agent.y = 0, 3
        #initialState.rocks[1].x, initialState.rocks[1].y = 0, 3
        initialState.rocks[1].x, initialState.rocks[1].y = 2,0
        initialState.rocks[2].x, initialState.rocks[2].y = 0,1
        initialState.rocks[3].x, initialState.rocks[3].y = 3,1
        initialState.rocks[4].x, initialState.rocks[4].y = 6,3
        initialState.rocks[5].x, initialState.rocks[5].y = 2,4
        initialState.rocks[6].x, initialState.rocks[6].y = 3,4
        initialState.rocks[7].x, initialState.rocks[7].y= 5,5
        initialState.rocks[8].x, initialState.rocks[8].y= 1,6

    elif n == 11 and k == 11:
        domain = Domain.Domain(n,k,rand)
        initialState = domain.makeInitialState()
        initialState.agent.x, initialState.agent.y = 0,5
        initialState.rocks[1].x, initialState.rocks[1].y =  0,3
        initialState.rocks[2].x, initialState.rocks[2].y = 0,7
        initialState.rocks[3].x, initialState.rocks[3].y = 1,8
        initialState.rocks[4].x, initialState.rocks[4].y = 2,4
        initialState.rocks[5].x, initialState.rocks[5].y = 3,3
        initialState.rocks[6].x, initialState.rocks[6].y = 3,8
        initialState.rocks[7].x, initialState.rocks[7].y = 4,3
        initialState.rocks[8].x, initialState.rocks[8].y = 5,8
        initialState.rocks[9].x, initialState.rocks[9].y = 6,1
        initialState.rocks[10].x, initialState.rocks[10].y = 9,3
        initialState.rocks[11].x, initialState.rocks[11].y = 9,9

    ##############
    rocks = initialState.rocks

    if debug > 1:
        print("Map Size:", n, "x", n)
        print("Rocks: ", k)
        print(initialState.agent.x, initialState.agent.y)
        for i, rock in rocks.items():
            print(rock.x, rock.y, rock.good)

    #generate domain
    domain.generateDomain(initialState)

    #simulated environment env?
    env = Environment.SimulatedEnvironment(domain, initialState)

    solver = Pomcp.Pomcp(debug, domain, pomcpParameters, rand)
    belief = Belief.belief()
    beliefEstimate = belief.pomcpSample(initialState, pomcpParameters.maxSamples, rand)
    root = solver.initializePomcp(initialState, beliefEstimate)

    particleDepletion = False
    actionCount = 0
    totalReward = 0
    discount = 1
    if debug > 1: env.simulator(n, k, initialState)
    while actionCount < pomcpParameters.maxActions:
        action = solver.selectAction(root)
        [s_, o, a, r, t] = env.executeAction(action)

        totalReward += discount * r
        discount *= pomcpParameters.pomcpDiscount #add discounted return

        if t: break;
        root = solver.beliefUpdate(root, a, o)

        if debug > 1:
            print("action: ", action)
            print("reward:", r)
            print(s_.agent.x, s_.agent.y)
            env.simulator(n,k,s_)
            if root != "particle Depletion":
                printBelief(root.beliefEstimate, k)


        if root == "particle Depletion":
            particleDepletion = True
            if debug > 1: print("PARTICLE DEPLETION")
            break
        actionCount += 1
        #bp()

    while particleDepletion and actionCount < pomcpParameters.maxActions:
        action = domain.selectRandomAction(env.s)
        [s_, o, a, r, t] = env.executeAction(action)
        if t: break
        actionCount += 1
        totalReward += r * discount
        discount *= pomcpParameters.pomcpDiscount

    return totalReward,particleDepletion


def printBelief(beliefEstimate, numRocks):
    l = len(beliefEstimate)
    print("root.belief has", l, " particles")

    distribution = {}
    for s in beliefEstimate:
        hashable_state = str(s)
        if hashable_state in distribution:
            distribution[hashable_state] += 1
        else:
            distribution[hashable_state] = 1

    for s in distribution:
        distribution[s] /= l
    for s in distribution:
        print(s + ": " + str(round(distribution[s], 3)))
