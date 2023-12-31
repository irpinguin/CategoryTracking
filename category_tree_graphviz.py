from graphviz import Digraph

def build_tree(dot, tree):
    for key, value in tree.items():
        node_id = f"{value['level']}_{key}"
        dot.node(node_id, label=value['name'])
        if value['subcategories']:
            build_tree(dot, value['subcategories'])
            dot.edge(node_id, f"{value['subcategories'].keys()}")

def visualize_tree(tree):
    dot = Digraph(comment='Category Tree')
    build_tree(dot, tree)
    dot.render('category_tree', format='png', cleanup=True)

# Пример использования
tree = {
    '1143372': {'level': 1, 'category_id_lvl_1': '1143372', 'name': 'Baikal Store', 'url': 'https://example.com/categories/1143372', 'subcategories': None},
    '11': {
        'level': 1,
        'category_id_lvl_1': '11',
        'name': 'Бытовая химия',
        'url': 'https://example.com/categories/11',
        'subcategories': {
            '127881': {'level': 2, 'category_id_lvl_2': '127881', 'name': 'Средства для мытья посуды', 'url': 'https://example.com/categories/127881', 'subcategories': {'655641': {'level': 3, 'category_id_lvl_3': '655641', 'name': 'Средства для посудомоечных машин', 'url': 'https://example.com/categories/655641', 'subcategories': None}, '655709': {'level': 3, 'category_id_lvl_3': '655709', 'name': 'Средства для мытья посуды', 'url': 'https://example.com/categories/655709', 'subcategories': None}}}, '127876': {'level': 2, 'category_id_lvl_2': '127876', 'name': 'Антистатики', 'url': 'https://example.com/categories/127876', 'subcategories': None}, '127886': {'level': 2, 'category_id_lvl_2': '127886', 'name': 'Чистящие средства', 'url': 'https://example.com/categories/127886', 'subcategories': None}
        }
    },
    '203131': {'level': 1, 'category_id_lvl_1': '203131', 'name': 'Товары для животных', 'url': 'https://example.com/categories/203131', 'subcategories': None}
}

visualize_tree(tree)
