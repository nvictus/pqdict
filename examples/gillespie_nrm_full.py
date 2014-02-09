from pqdict import PQDict
from numpy import array, zeros, log, seterr, isfinite, isnan
from numpy.random import rand
from collections import Counter
from matplotlib import pyplot as plt

seterr(divide='ignore')

#patt = re.compile(r'\b(\d*)(\w+)\b')

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
        - Use of dependency graph between reactions to prevent needless 
          rescheduling of reaction channels that are unaffected by an event.
        - Use of an indexed priority queue (pqdict) as a scheduler to achieve
          log(N) rescheduling.

    The paper describes an additional modification to cut down on the amount of 
    random number generation which was not implemented here for simplicity.

    """

    # initialize state
    t = tspan[0]
    x = initial_amounts
    T = [t]
    X = [x]
    a = {}
    
    # initialize scheduler
    scheduler = PQDict()
    for rxn in reactions:
        a[rxn] = rxn.propensity(x)
        tau = -log(rand())/a[rxn]   
        scheduler[rxn] = t + tau

    # first event
    rnext, tmin = scheduler.topitem()
    t = tmin
    x += rnext.stoich
    T.append( t )
    X.append( x.copy() )

    # main loop
    while t < tspan[1]:
        # reschedule
        a[rnext] = rnext.propensity(x)
        tau = -log(rand())/a[rnext]
        scheduler.updateitem(rnext, t + tau)        
        for rxn in dep_graph[rnext]:
            a_old = a[rxn]
            a[rxn] = rxn.propensity(x)
            if isfinite(scheduler[rxn]):
                tau = (a_old/a[rxn])*(scheduler[rxn] - t)
            else:
                tau = -log(rand())/a[rxn]
            scheduler.updateitem(rxn, t + tau)

        rnext, tmin = scheduler.topitem()

        # fire!
        t = tmin
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


