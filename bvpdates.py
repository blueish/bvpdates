import networkx as nx

names = [
    "Sam",
    "Riki",
    "Ohi",
    "Joe",
    ]

previous_pairings = [
        ("Sam", "Joe", 1),
        ("Ohi", "Riki", 1)
        ]

def create_pairing_edges(max_week):
    matchings = dict()
    for (n1, n2, week) in previous_pairings:
        weight = (max_week - week) ** 2
        # ensure ordering is respected to access later
        ordered_names = order_pair(n1, n2)
        matchings[ordered_names] = weight


    return matchings

def order_pair(a, b):
    if (a < b):
        return (a, b)

    return (b,a)


def main():
    G = nx.Graph();

    max_week = max(map(lambda t: t[2], previous_pairings)) + 1
    print(max_week)

    pair_map = create_pairing_edges(max_week)

    names_lenth = len(names);
    unmatched_edge_weight = names_lenth * (names_lenth - 1)

    for name1 in names:
        for name2 in names:
            if (not name1 == name2):
                (n1, n2) = order_pair(name1, name2)
                if ((n1, n2) in pair_map):
                    G.add_edge(n1, n2, weight=pair_map[(n1, n2)])
                else:
                    G.add_edge(n1, n2, weight=unmatched_edge_weight)


    # print(G.adj)
    print(nx.algorithms.max_weight_matching(G, True))



if __name__ == '__main__':
    main()

