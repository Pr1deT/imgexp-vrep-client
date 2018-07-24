import json

from libpgm.nodedata import NodeData
from libpgm.graphskeleton import GraphSkeleton
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork
from libpgm.pgmlearner import PGMLearner

# generate some data to use
nd = NodeData()
nd.load("bayes_structure.txt")    # an input file
skel = GraphSkeleton()
skel.load("bayes_structure.txt")
skel.toporder()
bn = DiscreteBayesianNetwork(skel, nd)
data = bn.randomsample(200)

# instantiate my learner 
learner = PGMLearner()

# estimate parameters from data and skeleton
result = learner.discrete_mle_estimateparams(skel, data)

# output
print json.dumps(result.Vdata, indent=2)