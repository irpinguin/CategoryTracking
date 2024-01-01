import ast
import json
import scipy
import networkx as nx
import matplotlib.pyplot as plt


def add_nodes(graph, node):
    for subcategory_id, subcategory_data in node.items():
        graph.add_node(subcategory_id, name=subcategory_data['name'])
        if subcategory_data['subcategories']:
            add_nodes(graph, subcategory_data['subcategories'])
            for subcategory_key in subcategory_data['subcategories']:
                graph.add_edge(subcategory_id, subcategory_key)


def visualize_tree(json_data):
    G = nx.DiGraph()
    add_nodes(G, json_data)

    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'name')

    nx.draw(G, pos, with_labels=True, labels=labels, node_size=700, font_size=8, font_color='black', font_weight='bold', node_color='skyblue', arrows=False)
    plt.show()


# Загрузка JSON из файла
with open('categories.txt', 'r', encoding='utf-8') as file:
    content = file.read()
    json_data = ast.literal_eval(content)

# Визуализация дерева
visualize_tree(json_data)
