from util import *
from collections import defaultdict
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
from scipy.stats import wasserstein_distance
import sys

###########################################################################
###########################################################################
#Get edge weights for node
###########################################################################
###########################################################################
def get_edge_weights(original_graph, attribute):

    # Create new graph using desired attribute
    graph = build_single_weight_graph(original_graph, attribute)

    edgeWeights = defaultdict(list)
    # Loop through all nodes, add attribute to each that is the sum of all adjacent edge weights
    for node in graph.Nodes():
        node_id, num_out_nodes = node.GetId(), node.GetOutDeg()
        degree = 0
        for i in range(num_out_nodes):
            neighbor_id = node.GetOutNId(i)
            edge_id = graph.GetEI(node_id, neighbor_id).GetId()
            weight = graph.GetFltAttrDatE(edge_id, 'weight')
            if weight > 0:
                edgeWeights[node_id].append(weight) # For some reason a few weights are -inf

    # Return
    return edgeWeights

def find_clusters(X, n_clusters, rseed=2):
        # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]

    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers, metric=wasserstein_distance)

        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0)
                                for i in range(n_clusters)])

        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers

    return centers, labels

###########################################################################
###########################################################################
# Compute and plot node degrees
###########################################################################
###########################################################################

def computePlotNodeDegrees(file_path_graph=FINAL_UBER_GRAPH_PATH, attributes=['travel_time', 'travel_speed']):
    # Compute / plot node degrees (sum of all adjacent edge weights)
    # Load graph
    FIn = snap.TFIn(file_path_graph)
    original_graph = snap.TNEANet.Load(FIn)
    # Compute node degree for various attributes
    for attribute in attributes:
        for hour in range(24):
            attribute_hour = attribute + '_' + str(hour)
            new_graph = compute_node_degree(original_graph, attribute_hour)
            # Plot
            draw_map('Data/Geo/Images/uber_%s/%s.png'%(attribute, attribute_hour), \
                        plot_centroids=True, scale_centroids=True, graph=new_graph)

def computePlotNodeDegreesPublicTransit(file_path_graph, attributes):
    # Compute / plot node degrees (sum of all adjacent edge weights)
    # Load graph
    FIn = snap.TFIn(file_path_graph)
    original_graph = snap.TNEANet.Load(FIn)
    # Compute node degree for various attributes
    for attribute in attributes:
        new_graph = compute_node_degree(original_graph, attribute)
        # Plot
        draw_map('Data/Geo/Images/PublicTransit_%s.png'%(attribute), \
                    plot_centroids=True, scale_centroids=True, graph=new_graph)

###########################################################################
###########################################################################
# Plot degree distribution
###########################################################################
###########################################################################
def plotDegreeDistribution(original_graph, attribute, type_graph = "google"):

    graph = compute_node_degree(original_graph, attribute)
    weights = []
    for node in graph.Nodes():
        weight = graph.GetFltAttrDatE(node.GetId(), "weight")
        weights.append(weight)

    graph = compute_node_degree(original_graph, attribute)
    weights = []
    for node in graph.Nodes():
        weight = graph.GetFltAttrDatE(node.GetId(), "weight")
        weights.append(weight)


    # Create some example data

    # Usual histogram plot
    # Scatter plot
    # Now we find the center of each bin from the bin edges
    plt.figure()
    n, bins, patches = plt.hist(weights, bins=100)  # output is two arrays
    bins_mean = [0.5 * (bins[i] + bins[i+1]) for i in range(len(n))]

    plt.figure()
    plt.scatter(bins_mean, n, label="Degree distribution for " +type_graph + " " + attribute)
    # plt.xscale('log')
    # plt.yscale('log')


    plt.hist(weights, bins=50, log=True)
    plt.xlabel('Node Degree (log)')
    plt.ylabel('# Nodes with a Given Degree (log)')
    plt.title('Degree Distribution ')
    plt.legend()
    plt.grid(which='both', axis='both')
    plt.savefig("Data/Geo/Images/degree_distribution_"+type_graph+"_"+attribute+".png")
    plt.show()

###########################################################################
###########################################################################
# Main function
###########################################################################
###########################################################################
def main():

    # [Uber] Compute / plot node degrees (sum of all adjacent edge weights)
    if False:
        computePlotNodeDegrees(file_path_graph=FINAL_UBER_GRAPH_PATH, attributes=['travel_time', 'travel_speed'])

    # [Google] Compute / plot node degrees (sum of all adjacent edge weights)
    if False:
        computePlotNodeDegreesPublicTransit(file_path_graph=FINAL_GOOGLE_GRAPH_PATH, attributes=['distance_meters', 'duration_seconds'])

    # Compute average node degree over time
    if False:
        # Load graph
        FIn = snap.TFIn(FINAL_UBER_GRAPH_PATH)
        original_graph = snap.TNEANet.Load(FIn)
        # Compute node degree for various attributes
        attributes = [('travel_time', 'minutes'), ('travel_speed', 'mph')]
        results = []
        for attribute, label in attributes:
            # Compute
            temp = []
            for hour in range(24):
                new_graph = compute_node_degree(original_graph, attribute+'_'+str(hour), average=True)
                avg_degree = 0
                for node in new_graph.Nodes():
                    avg_degree += new_graph.GetFltAttrDatN(node.GetId(), 'weight')
                avg_degree /= float(new_graph.GetNodes())
                if attribute == 'travel_time': avg_degree /= 60.0
                print('[%d] %.2f' % (hour, avg_degree))
                temp.append(avg_degree)
            # Save
            results.append(temp)
        # Plot
        plt.figure(figsize=(30,20))
        # Time
        fig, ax1 = plt.subplots()
        ax1.plot(range(24), results[0], 'b-')
        ax1.set_ylabel('Avg Travel Time (mins)', color='b')
        ax1.tick_params('y', colors='b')
        # Speed
        ax2 = ax1.twinx()
        ax2.plot(range(24), results[1], 'r-')
        ax2.set_ylabel('Avg Travel Speed (mph)', color='r')
        ax2.tick_params('y', colors='r')
        # Overall
        ax1.set_xlabel('Hour of Day')
        ax1.set_xticks(range(24))
        plt.title('Avg Travel Time vs. Avg Travel Speed for Each Hour of Day')
        plt.savefig('Data/Geo/Images/uber_avg_time_vs_avg_speed.png', dpi=300)

    if False:
        FIn = snap.TFIn(FINAL_UBER_GRAPH_PATH)
        original_graph = snap.TNEANet.Load(FIn)
        edgeWeightDistributions = []
        attributes = ['travel_time_12']
        for attribute in attributes:
            edgeWeights = get_edge_weights(original_graph, attribute)
            #1. Convert each node array of edges to histogram
                #Find global min and max values of weights
            minWeight = min([min(weights) for node, weights in edgeWeights.iteritems()])
            maxWeight = max([max(weights) for node, weights in edgeWeights.iteritems()])
            edgeWeightHistograms = {}
            for node, weights in edgeWeights.iteritems():
                histo = np.histogram(weights, bins=[  21.65,341.75083333,661.85166667,981.9525,1302.05333333, 1622.15416667, 1942.255, 2262.35583333,2582.45666667, 2902.5575,3222.65833333,3542.75916667,3862.86],
                    range=(minWeight, maxWeight))
                edgeWeightHistograms[node] = list(histo[0])

            nodes, histograms = zip(*edgeWeightHistograms.iteritems())
            centers, labels = find_clusters(np.array(histograms), 3)
            node_roles = dict(zip(nodes, labels))
            draw_map(attribute+'_node_roles', plot_centroids=True, centroid_classes=node_roles)




if __name__ == "__main__":
    main()
