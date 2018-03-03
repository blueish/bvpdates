import networkx as nx
import csv

# names = [
#     "Sam",
#     "Riki",
#     "Ohi",
#     "Joe",
#     "Bob"
#     ]

# previous_pairings = [
#         ("Sam", "Joe", 1),
#         ("Ohi", "Riki", 1),
#         ("Sam", "Riki", 2),
#         ("Joe", "Ohi", 2),
#         ("Ohi", "Sam", 3),
#         ("Bob", "Riki", 3)
#         ]



def get_names_and_pairings():
    """Generate a tuple of names and previous pairings from CSV

    Parameters:
    ----------
    file_name: String

    Assumptions:
    ------------
    The file is a well formatted CSV file, with the following properties:
        1. The first column header is 'Name'
        2. The column indexes are integers
        3. Each name that appears in the dataset is one of the names found
            in the 'Name' column

    """
    previous_pairings = {}
    names = []

    seen_names = {} #dict to validate the dataset to keep track of names we saw

    with open('BVP Dates.csv') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            name = row['Name']
            name = name.strip().replace(' ', '').lower()
            names.append(name)
            seen_names[name] = True

            for (week, pairing_name) in row.items():
                pairing_name = pairing_name.strip().replace(' ', '').lower()

                # skip, if it's the name key
                if not week == 'Name':
                    week_number = int(week)
                    ordered_names = order_pair(name, pairing_name)

                    if not pairing_name in names:
                        seen_names[pairing_name] = week_number

                    previous_pairings[ordered_names] = week_number

    # validate the names:
    for name in names:
        del seen_names[name]

    if len(seen_names) > 0:
        print('We found names that were not matched with labels. ',
              'Please validate your dataset!')
        print('Names found were: ', seen_names.items())

    return (names, previous_pairings)




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
    (names, previous_pairings) = get_names_and_pairings()

    G = nx.Graph();

    max_week = max(map(lambda t: t[2], previous_pairings)) + 1
    print(max_week)

    pair_map = create_pairing_edges(max_week)


    names_lenth = len(names);
    unmatched_edge_weight = names_lenth * (names_lenth - 1)

    for name1 in names:
        for name2 in names:
            if not name1 == name2:
                (n1, n2) = order_pair(name1, name2)
                if ((n1, n2) in pair_map):
                    G.add_edge(n1, n2, weight=pair_map[(n1, n2)])
                else:
                    G.add_edge(n1, n2, weight=unmatched_edge_weight)


    print(nx.algorithms.max_weight_matching(G, True))



if __name__ == '__main__':
    main()

