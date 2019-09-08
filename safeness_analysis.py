# -*- coding: utf-8 -*-
"""Safeness Analysis

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HFZYa5_FB8NOMurBpvkrMbuQM0XFhIjw
"""

# Commented out IPython magic to ensure Python compatibility.
# Load the Drive helper and mount
from google.colab import drive

# This will prompt for authorization.
drive.mount('/content/Drive2')

# %cd "/content/Drive2/My Drive/BTP/"
!ls

import igraph
import networkx as nx
import copy
import random
import matplotlib.pyplot as plt

# forming an adjacency list for the graph - undirected graph with 0 indexed nodes
def get_adj_list(E):
	Adjacency_List = {}
	for i in range (0, len(E)):
		e = E[i]
		s = e[0]
		t = e[1]
		if (s - 1 in Adjacency_List.keys()):
			Adjacency_List[s - 1].append(t - 1)
		else:
			Adjacency_List[s - 1] = []
			Adjacency_List[s - 1].append(t - 1)
		if (t - 1 in Adjacency_List.keys()):
			Adjacency_List[t - 1].append(s - 1)
		else:
			Adjacency_List[t - 1] = []
			Adjacency_List[t - 1].append(s - 1)
	return Adjacency_List

# the community deception algorithm
def com_decept_safeness(target_comm, communities, IG_edgeList, beta, deg, out_deg, out_ratio, num_vertices, new_adj, new_edge_list, intra_considered):
	add_gain = 0
	del_gain = 0
	while(True):
		node_list = get_min_NodeRatio_index(out_ratio)
		(add_gain, add_node_ind) = min_index_edge_addition(node_list, deg, out_deg)
		add_node = target_comm[add_node_ind]
		add_node_2 = findExternalNode(add_node, target_comm, communities, IG_edgeList)
		li = getBestDelExclBridges(target_comm, new_edge_list, new_adj, num_vertices)
		((del_node, del_node_2), max_gain) = deletion_Gain(li, intra_considered, deg, out_deg, target_comm)
		del_gain = max_gain
		if add_gain >= del_gain and add_gain > 0:
			print ("Gain - " + str(add_gain))
			print ("Edge Added - (" + str(add_node) + ", " + str(add_node_2) + ")")
			IG_edgeList.append((add_node, add_node_2))

			for i in target_comm:
				deg_ = 0
				out_deg_ = 0
				for j in IG_edgeList:
					if i == j[0] or i == j[1]:
						deg_ = deg_ + 1
						if (i == j[0] and j[1] not in target_comm) or (i == j[1] and j[0] not in target_comm):
							out_deg_ = out_deg_ + 1
				deg[target_comm.index(i)] = deg_
				out_deg[target_comm.index(i)] = out_deg_

			for i in range (0, len(out_ratio)):
				out_ratio[i] = out_deg[i]/deg[i]

		elif del_gain > 0:
			print ("Gain - " + str(del_gain))
			print ("Edge Deleted - (" + str(del_node) + ", " + str(del_node_2) + ")")
			IG_edgeList.remove((del_node,del_node_2))
			intra_considered.append((del_node,del_node_2))

			for i in target_comm:
				deg_ = 0
				out_deg_ = 0
				for j in IG_edgeList:
					if i == j[0] or i == j[1]:
						deg_ = deg_ + 1
						if (i == j[0] and j[1] not in target_comm) or (i == j[1] and j[0] not in target_comm):
							out_deg_ = out_deg_ + 1
				deg[target_comm.index(i)] = deg_
				out_deg[target_comm.index(i)] = out_deg_

			for i in range (0, len(out_ratio)):
				out_ratio[i] = out_deg[i]/deg[i]

			new_edge_list.remove((del_node, del_node_2))
			new_adj[del_node].remove(del_node_2)
			new_adj[del_node_2].remove(del_node)

		beta = beta - 1

		if (beta > 0 and (add_gain > 0 or del_gain > 0)):
			continue
		else:
			break
	return IG_edgeList

# for inter edge addition get the node with the minimum ratio of out degree/degree
def get_min_NodeRatio_index(out_ratio):

	min_val = min(out_ratio)
	node = []
	for i in range (0, len(out_ratio)):
		if out_ratio[i] == min_val:
			node.append(i)
	return node

# for finding the safeness gain for inter edge addition - of the node obtained from get_min_NodeRatio_index method
def min_index_edge_addition(node_list, deg, out_deg):

	node_ind = 0
	max_gain = 0
	for i in node_list:
		gain = 0.5*((out_deg[i]+1)/(deg[i]+1)-out_deg[i]/deg[i]) 
		if gain > max_gain:
			max_gain = gain
			node_ind = i
	return (max_gain, node_ind)

# for finding a node in a community other than the target for edge addition
def findExternalNode(com_node, com, graph, edges):
	for i in graph:
		if i != com:
			for j in i:
				if ((com_node, j) or (j, com_node)) not in edges:
					return j

# finding the intra edge with the maximum safeness gain
def deletion_Gain(li, intra_considered, deg, out_deg, target_comm):							

	max_gain = 0
	node_u = 0
	node_v = 0
	for i in li:
		if i not in intra_considered:
			u = i[0]
			v = i[1]
			gain = (out_deg[target_comm.index(u)]/(2*deg[target_comm.index(u)]*(deg[target_comm.index(u)]-1)))+(out_deg[target_comm.index(v)]/(2*deg[target_comm.index(v)]*(deg[target_comm.index(v)]-1))) + (1/(len(target_comm) - 1))
			if(gain > max_gain):
				max_gain = gain
				node_u = u
				node_v = v
	return ((node_u, node_v), max_gain)

# get the non bridging edges
def getBestDelExclBridges(target_comm, edges, Adjacency_List, num_vertices):
	
	best_edges = []
	for i in edges:
		Cpy_Adj_List = copy.deepcopy(Adjacency_List)
		Cpy_Adj_List[i[0]].remove(i[1])
		Cpy_Adj_List[i[1]].remove(i[0])
		try:
			if(connectedComponents(target_comm, num_vertices, Cpy_Adj_List)) == 1:
				best_edges.append(i)
		except:
			continue
	return best_edges

# calculating the number of components for the subgraph spanned by vertices of target community
def DFSUtil(target_comm, temp, v, visited, Adjacency_List):

	visited[v] = True
	temp.append(v)
	for i in Adjacency_List[target_comm[v]]:
		if visited[target_comm.index(i)] == False:
			temp = DFSUtil(target_comm, temp, target_comm.index(i), visited, Adjacency_List)
	return temp

def connectedComponents(target_comm, num_vertices, Adjacency_List):
	visited = [] 
	cc = [] 
	for i in range(num_vertices):
		visited.append(False)
	for v in range(num_vertices):
		if visited[v] == False: 
			temp = [] 
			cc.append(DFSUtil(target_comm, temp, v, visited, Adjacency_List))
	return len(cc)

def vertices_in_connectedComponents(target_comm, num_vertices, Adjacency_List, node):
	visited = [] 
	cc = [] 
	for i in range(num_vertices):
		visited.append(False)
	for v in range(num_vertices):
		if visited[v] == False: 
			temp = [] 
			cc.append(DFSUtil(target_comm, temp, v, visited, Adjacency_List))
	cc_node_list=[]
	for i in cc:
		tmp=[]
		for j in i:
			tmp.append(target_comm[j])
		cc_node_list.append(tmp)

	for i in cc_node_list:
		if (node in i):
			return len(i)
	return 0

# reading the dataset
graph = nx.read_gml('karate.gml', label = "id")
graph2 = nx.read_gml('karate.gml', label = "id")

e_ = list(graph.edges)
e2_ = list(graph2.edges)

Adjacency_List = get_adj_list(e_)
Adjacency_List2 = get_adj_list(e2_)

g = igraph.Graph(directed = False)
g2 = igraph.Graph(directed = False)

num_vertices = 34

g.add_vertices(num_vertices)
g2.add_vertices(num_vertices)

IG_edgeList = [] # 0 indexed edge list

for i in e_:
	IG_edgeList.append((i[0] - 1, i[1] - 1)) 

IG_edgeList2 = IG_edgeList[:] # 0 indexed edge list

g.add_edges(IG_edgeList)
g2.add_edges(IG_edgeList2)

communities = g.community_multilevel()
communities2 = copy.deepcopy(communities)
comm_1 = copy.deepcopy(communities)
safe_copy_comm = copy.deepcopy(communities)

comm_length = len(communities)

print (communities)
print ()
	
NMI_List = []
for i in range(comm_length):
	graph = nx.read_gml('karate.gml', label = "id")
	graph2 = nx.read_gml('karate.gml', label = "id")

	e_ = list(graph.edges)
	e2_ = list(graph2.edges)

	Adjacency_List = get_adj_list(e_)
	Adjacency_List2 = get_adj_list(e2_)

	g = igraph.Graph(directed = False)
	g2 = igraph.Graph(directed = False)

	num_vertices = 34

	g.add_vertices(num_vertices)
	g2.add_vertices(num_vertices)

	IG_edgeList = [] # 0 indexed edge list

	for j in e_:
		IG_edgeList.append((j[0] - 1, j[1] - 1)) 

	IG_edgeList2 = IG_edgeList[:] # 0 indexed edge list

	g.add_edges(IG_edgeList)
	g2.add_edges(IG_edgeList2)

	target_comm = communities[i] # selecting a target community
	target_comm2 = communities2[i]
  
	print ("Target Community - " + str(target_comm))

	deg = []
	for j in target_comm:
		deg.append(g.vs[j].degree()) # getting the degree for every node

	deg2 = copy.deepcopy(deg)

	out_deg = []

	for j in target_comm:
		out_ = 0
		for k in Adjacency_List[j]:
			if (k) not in target_comm:
				out_ = out_ + 1
		out_deg.append(out_) # getting the out degree for every node

	out_deg2 = copy.deepcopy(out_deg)

	out_ratio = []
	for j in range (0, len(out_deg)):
		out_ratio.append(out_deg[j]/deg[j]) # calculating out ratio for every node

	out_ratio2 = out_ratio[:]

	# target community members subgraph
	new_adj = {}
	for j in Adjacency_List.keys():
		if j in target_comm:
			new_adj[j] = []
			for k in Adjacency_List[j]:
				if k in target_comm:
					new_adj[j].append(k)

	new_adj2 = copy.deepcopy(new_adj)

	new_edge_list = []
	for j in IG_edgeList:
		if j[0] in target_comm and j[1] in target_comm:
			new_edge_list.append(j)

	beta = 4
	intra_considered = []

	IG_edgeList_ = com_decept_safeness(target_comm, communities, IG_edgeList, beta, deg, out_deg, out_ratio, len(target_comm), new_adj, new_edge_list, intra_considered)

	# communities in the updated graph
	g = igraph.Graph(directed = False)
	num_vertices = 34
	g.add_vertices(num_vertices)
	g.add_edges(IG_edgeList_)
	communities = g.community_multilevel()

	print (communities)
  
	before_mem = []
	for node in target_comm:
		for grp in range(0, len(comm_1)):
			if node in comm_1[grp]:
				before_mem.append(grp)
				break

	after_mem = []
	for node in target_comm:
		for grp in range(0, len(communities)):
			if node in communities[grp]:
				after_mem.append(grp)
				break
        
	mem_list = []
	for mem in after_mem:
		if mem not in mem_list:
				mem_list.append(mem)

	# calculting the NMI score
	nmi = igraph.compare_communities(comm_1, communities, method = "nmi")
	
	print ("NMI - " + str(nmi))
	print ()
  
	NMI_List.append(nmi)
	communities = safe_copy_comm
	
print(sum(NMI_List)/len(NMI_List))