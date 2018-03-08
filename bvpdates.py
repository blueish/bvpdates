import networkx as nx
import csv


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
    max_week = 0

    seen_names = {} #dict to validate the dataset to keep track of names we saw

    with open('test_dataset.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            name = row['Name']
            name = name.strip().replace(' ', '').lower()
            names.append(name)
            seen_names[name] = True

            for (week, pairing_name) in row.items():
                pairing_name = pairing_name.strip().replace(' ', '').lower()

                # skip, if it's the name key
                if week != '' and not week == 'Name':
                    week_number = int(week)
                    if week_number > max_week:
                        max_week = week_number

                    ordered_names = order_pair(name, pairing_name)
                    previous_pairings[ordered_names] = week_number

                    if not pairing_name in names:
                        seen_names[pairing_name] = week_number

    # validate the names:
    for name in names:
        del seen_names[name]

    # we'll have 1 'unmatched' with the empty (missing) case if we're missing any
    # historical data, so ignore it 
    if len(seen_names) > 0 and not '' in seen_names:
        print('We found names that were not matched with labels. ',
              'Please validate your dataset!')
        print('Names found were: ', seen_names)

    return (names, previous_pairings, max_week)



def order_pair(a, b):
    if (a < b):
        return (a, b)

    return (b,a)


def main():
    (names, previous_pairings, max_week) = get_names_and_pairings()

    G = nx.Graph();

    names_lenth = len(names);
    unmatched_edge_weight = names_lenth * (names_lenth - 1)

    for name1 in names:
        for name2 in names:
            if not name1 == name2:
                (n1, n2) = order_pair(name1, name2)
                if ((n1, n2) in previous_pairings):
                    adjusted_weight = (max_week - previous_pairings[(n1, n2)]) ** 2
                    G.add_edge(n1, n2, weight=adjusted_weight)
                else:
                    G.add_edge(n1, n2, weight=unmatched_edge_weight)


    greatest_matching = nx.algorithms.max_weight_matching(G, True)

    if (True):
        print('Respective weights: (if not all same, some suboptimal matches')
        for (name1, name2) in greatest_matching:
            print(G[name1][name2])

    print('You should pair these people together this week:')
    for (name1, name2) in greatest_matching:
        print(name1 + ', ' + name2)



if __name__ == '__main__':
    main()

