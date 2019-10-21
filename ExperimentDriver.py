import PomcpDriver as driver
import PomdpConfiguration as pomdp
import sys
import random
import os
import time
import csv

import click  # Command Line Interface Creation Kit
@click.command()
@click.option('--out', required=True, type=str, help='Name of output directory')
@click.option('--exp', required=True, type=str, help='Name of experiment')
@click.option('--iterations', required=True, type=int, help='Number of experiment iterations')
@click.option('--n', required=True, type=int, help='Domain size')
@click.option('--k', required=True, type=int, help='Rocks')
@click.option('--sim', required=True, type=int, help='Pomcp: Number of Simulations')
@click.option('--act', required=True, type=float, help='Pomcp: Max Number of Actions')
@click.option('--horizon', required=True, type=float, help='Pomcp: Horizon Depth')
@click.option('--uct', required=True, type=float, help='Pomcp: UCT exploration parameter')
#--out Out --exp rocksample_normal --iterations 1 --n 11 --k 11 --sim 1000 --act 100 --horizon 20 --uct 2.0
def experimentDriver(out, exp, method, iterations, n, k,
                     sim, act, horizon, uct):
    # ------------------Parameters----------------------
    #Fixed Parameters
    pomcpReinvigorateSamples = 0
    pomcpExploration = uct
    pomcpDiscount = 0.95

    debug = 3 #0: no print, 1: domain / final reward, 2: simulator / belief, 3: q-values
    experimentReady = False #sets rand
    print("hey")

    if experimentReady: debug = 1

    PomcpParameters = pomdp.PomcpParameters(sim, act, horizon, pomcpReinvigorateSamples, pomcpExploration,
                                            pomcpDiscount)
    expTime = []
    expReward = []
    # ------------------POMDP Program----------------------
    experimentHeader = str(exp + " : n=" + str(n) + " k=" + str(k) + " method=" + str(method) +
                           " sim=" + str(sim) + " act=" + str(act) + " horizon=" + str(horizon) + " uct=" + str(uct))
    print("Experiment Condition:" + experimentHeader)

    for e in range(iterations):
        rand = random.Random() if experimentReady else random.Random(0)  # set to random.Random() or random.Random(0) for stochastic / deterministic setting
        start = time.time()

        trialDicountedReward, particleDepletion = driver.executeSearchWorld(debug, rand, n, k, PomcpParameters)

        expTime.append(time.time() - start)
        expReward.append(trialDicountedReward)

        if debug > 0:
            print("exp:" + str(e) + " Reward: " + str(trialDicountedReward))
            print("exp:" + str(e) + " Particle Depletion: " + str(particleDepletion))

    if experimentReady:
        dl_path = os.path.join(os.getcwd(), out)

        if not os.path.exists(dl_path):
            os.makedirs(dl_path)

        #organization of output file is n rows for each belief condition with m columns for experiments
        with open(dl_path + "/" + exp + ".csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(expReward)


if __name__ == '__main__':
    experimentDriver()
