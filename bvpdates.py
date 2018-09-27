import networkx as nx
import csv
import sys


def old_get_pairings(filename):
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

    Returns:
    -------
    Tuple of (names, previous pairings, current week number)
    """
    previous_pairings = {}
    names = []
    max_week = 0

    seen_names = {} # keep track of names we've seen to validate

    with open(filename) as f:
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
    # historical data, so ignore it, otherwise warn about malformed data
    if len(seen_names) > 0 and not '' in seen_names:
        print('We found names that were not matched with labels. ',
              'Please validate your dataset!')
        print('Names found were: ', seen_names)

    return (names, previous_pairings, max_week)



# TODO: merge both this and creation of graph
def new_get_pairings(filename):
    previous_pairings = {}
    names = set()
    max_week = 0

    seen_names = {} # keep track of names we've seen to validate

    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            week = row['Week']
            week = int(week)
            if week > max_week:
                max_week = week

            for (a, b) in row.items():
                if 'Week' not in a:
                    # clean the names
                    a = a.strip().replace(' ', '').lower()
                    b = b.strip().replace(' ', '').lower()
                    names.add(a)
                    names.add(b)
                    if not a in seen_names:
                        seen_names[a] = b
                    if not b in seen_names:
                        seen_names[b] = a

                    # skip, if it's the name key
                    ordered_names = order_pair(a, b)
                    previous_pairings[ordered_names] = week

    # validate the names:
    for name in names:
        del seen_names[name]

    # we'll have 1 'unmatched' with the empty (missing) case if we're missing any
    # historical data, so ignore it, otherwise warn about malformed data
    if len(seen_names) > 0 and not '' in seen_names:
        print('We found names that were not matched with labels. ',
              'Please validate your dataset!')
        print('Names found were: ', seen_names)

    sorted_names = list(names)
    sorted_names.sort()

    return (sorted_names, previous_pairings, max_week)
    

def order_pair(a, b):
    if (a < b):
        return (a, b)

    return (b,a)


def append_csv(filename, names, new_week, name_pairings):
    names.sort()
    fieldnames = ['Week'] + names

    with open(filename, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, lineterminator='\n', delimiter=',')
        # writer.writeheader()
        new_row = {'Week': new_week }
        for (a, b) in name_pairings:
            new_row[a] = b
            new_row[b] = a

        writer.writerow(new_row)


def create_graph(names, previous_pairings, max_week):
    G = nx.Graph();

    unmatched_edge_weight = max_week * (max_week + 1)

    # create matches for all names we have
    # O(n^2), but we don't have a choice
    for name1 in names:
        for name2 in names:
            # don't match the same people together!
            if not name1 == name2:
                # We order here just to maintain our previous pairings
                (n1, n2) = order_pair(name1, name2)
                if ((n1, n2) in previous_pairings):
                    adjusted_weight = (max_week - previous_pairings[(n1, n2)]) ** 2
                    G.add_edge(n1, n2, weight=adjusted_weight)
                else:
                    G.add_edge(n1, n2, weight=unmatched_edge_weight)

    return G

def main(filename):
    (names, previous_pairings, max_week) = new_get_pairings(filename)

    G = create_graph(names, previous_pairings, max_week)

    greatest_matching = nx.algorithms.max_weight_matching(G, True)

    if (True):
        print('Respective weights: (if not all same, some suboptimal matches')
        for (name1, name2) in greatest_matching:
            print(G[name1][name2])

    print('You should pair these people together this week:')
    for (name1, name2) in greatest_matching:
        print(name1 + ', ' + name2)

    print('writing pairs to new_output to pair...')
    append_csv(filename, names, max_week + 1 ,greatest_matching)
    print('done')



if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)

