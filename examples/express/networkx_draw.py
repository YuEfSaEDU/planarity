import planarity
import networkx as nx


G=nx.wheel_graph(10)

# Increase the figsize due to the graph having more vertices.
planarity.draw(graph=G, outfileName='wheel.png',
               vertex_bordercolor='black', figsize=(8,6))
