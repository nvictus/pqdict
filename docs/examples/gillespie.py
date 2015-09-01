from pqdict import PQDict
from numpy import array, zeros, log, seterr
from numpy.random import rand
from collections import Counter
from matplotlib import pyplot as plt

seterr(divide='ignore')

class Reaction(object):
    def __init__(self, stoich, rate_const, idx):
        self.rate_const = rate_const
        self.stoich = stoich
        self.idx = idx

    def propensity(self, state):
        raise NotImplementedError

class ZerothOrderReaction(Reaction):
    def propensity(self, state):
        return self.rate_const

class UnimolecularReaction(Reaction):
    def propensity(self, state):
        x = state[self.idx]
        return self.rate_const*x[0]

class HomogeneousBimolecularReaction(Reaction):
    def propensity(self, state):
        x = state[self.idx]
        return self.rate_const*x[0]*(x[0]-1)/2

class BimolecularReaction(Reaction):
    def propensity(self, state):
        x = state[self.idx]
        return self.rate_const*x[0]*x[1]

def create_reaction(species_list, reactants_str, products_str, rate_const):
    """
    Return an object representing a type of chemical reaction (sometimes called
    a reaction "channel").
    
    Input:
        species_list: list of names of allowed chemical species
        reactants_str, products_str: 
            Names of reactant and product species, separated by whitespace. 
            Stoichiometries greater than one are denoted by repeating a name 
            multiple times. (e.g. 'TetR TetR' for a dimerization reaction).
        rate_const: the stochastic rate constant

    Returns:
        Reaction object

    """
    n = len(species_list)
    reactants = reactants_str.split()
    products  = products_str.split()
    count = Counter(products)
    count.subtract(Counter(reactants))
    assert all(sp in species_list for sp in count), "Unknown chemical species."

    # Create the stoichiometry vector
    stoich = zeros(n, dtype=int)
    for sp in count:
        stoich[species_list.index(sp)] = count[sp]

    # Indices of reactants in the state vector
    idx = array([species_list.index(r) for r in reactants], dtype=int)

    # Rate constant    
    rate_const = float(rate_const)

    # Choose the appropriate reaction rate law
    mol = len(reactants)
    if mol == 0:
        rxn = ZerothOrderReaction(stoich, rate_const, idx)
    elif mol == 1:
        rxn = UnimolecularReaction(stoich, rate_const, idx)
    elif mol == 2:
        if reactants[0] == reactants[1]:
            rxn = HomogeneousBimolecularReaction(stoich, rate_const, idx)
        else:
            rxn = BimolecularReaction(stoich, rate_const, idx)
    else:
        raise ValueError("Only 0th, 1st, and 2nd order reactions are allowed.")

    return rxn

def gillespie_nrm(tspan, initial_amounts, reactions, dep_graph):
    """
    Implementation of the "Next-Reaction Method" variant of the Gillespie 
    stochastic simulation algorithm, described by Gibson and Bruck. 

    The main enhancements are:
        - Use of dependency graph connecting the reaction channels to prevent 
          needless rescheduling of reactions that are unaffected by an event.
        - Use of an indexed priority queue (pqdict) as a scheduler to achieve
          O(log(M)) rescheduling on each iteration, where M is the number of
          reactions, assuming the dependency graph is sparse.

    The paper describes an additional modification to cut down on the amount of 
    random number generation which was not implemented here for simplicity.

    """
    # initialize state
    t = tspan[0]
    x = initial_amounts
    T = [t]
    X = [x]
    
    # initialize scheduler
    scheduler = PQDict()
    for rxn in reactions:
        tau = -log(rand())/rxn.propensity(x) 
        scheduler[rxn] = t + tau

    # first event
    rnext, tnext = scheduler.topitem()
    t = tnext
    x += rnext.stoich
    T.append( t )
    X.append( x.copy() )

    # main loop
    while t < tspan[1]:
        # reschedule
        tau = -log(rand())/rnext.propensity(x)
        scheduler[rnext] = t + tau

        # reschedule dependent reactions
        for rxn in dep_graph[rnext]:
            tau = -log(rand())/rxn.propensity(x)
            scheduler[rxn] = t + tau
        
        # fire the next one!
        rnext, tnext = scheduler.topitem()
        t = tnext
        x += rnext.stoich
        T.append( t )
        X.append( x.copy() )

    return array(T), array(X)


if __name__ == '__main__':
    species = [
        'mRNA', 
        'protein',
    ]

    reactions = [
        create_reaction(species, '', 'mRNA', 0.1),
        create_reaction(species, 'mRNA', 'mRNA protein', 0.1),
        create_reaction(species, 'mRNA', '', 0.1),
        create_reaction(species, 'protein', '', 0.002),
    ]

    dependencies = {
        reactions[0]: (reactions[1], reactions[2]),
        reactions[1]: (reactions[3],),
        reactions[2]: (reactions[1],),
        reactions[3]: (),
    }

    tspan = (0, 10000)
    initial_amounts = array([0, 0], dtype=int)
    
    T, X = gillespie_nrm(tspan, initial_amounts, reactions, dependencies)

    plt.plot(T, X)
    plt.xlabel('time (s)')
    plt.ylabel('number of molecules')
    plt.xlim(tspan)
    plt.show()


