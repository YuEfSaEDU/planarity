"""Run from the desired output directory to generate seven color examples."""

import planarity


edgelist = [('a', 'c'), ('a', 'd'), ('a', 'e'), ('b', 'c'), ('b', 'd'),
            ('b', 'e'), ('c', 'd'), ('c', 'e'), ('d', 'e')]

colors = {
    'facecolor': 'lightyellow',
    'transparent': True,
    'vertex_facecolor': 'lightgreen',
    'vertex_bordercolor': 'black',
    'vertex_label_facecolor': 'lavender',
    'vertex_label_bordercolor': 'red',
    'edge_linecolor': 'darkorange',
}

for property_name, value in colors.items():
    planarity.draw(
        edgelist,
        outfileName=f'K5-minus-edge_{property_name}.png',
        **{property_name: value},
    )
