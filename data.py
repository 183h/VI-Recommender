from pandas import read_csv
from timeit import default_timer
from cPickle import dump
from scipy.stats.stats import pearsonr
from math import isnan
from numpy import array, reshape


def prep_data(df_activities, df_deals, df_items, similarity, c_k):
    start = default_timer()

    users_unique = df_activities['user_id'].unique()
    users_unique.sort()
    items_unique = [i for i in df_items['id']]
    items_unique.sort()

    users = {}
    items = {}
    similarities = {}
    stats = []

    s1 = default_timer()
    for i in items_unique:
        for i_b in df_activities[['user_id', 'quantity']][df_activities['dealitem_id'] == i].itertuples():
            index, u_id, quantity = i_b

            try:
                items[i][u_id] += quantity
            except KeyError:
                items.setdefault(i, {})[u_id] = quantity

    dump(items, open("items_itembased1.p", "wb"))
    e1 = default_timer()
    # print "Items exec time", (e1 - s1) / 60, "min"

    s2 = default_timer()
    for u in users_unique:
        for i in df_activities[['dealitem_id', 'quantity']][df_activities['user_id'] == u].itertuples():
            index, i_id, quantity = i
            try:
                users[u][i_id] += quantity
            except KeyError:
                users.setdefault(u, {})[i_id] = quantity

    dump(users, open("users_itembased1.p", "wb"))
    e2 = default_timer()
    # print "Users exec time", (e2 - s2) / 60, "min"

    s3 = default_timer()
    for i in items:
        similarities[i] = []
        for ii in items:
            if i != ii:
                common_keys = [k for k in items[i] if k in items[ii]]
                if common_keys and len(common_keys) >= c_k:
                    if similarity.__name__ == 'cosine_similarity':
                        i1 = array([items[i][k] for k in common_keys])
                        i2 = array([items[ii][k] for k in common_keys])
                        t_sim = similarity(i1.reshape(1, -1), i2.reshape(1, -1))
                        sim = t_sim[0][0]
                    elif similarity.__name__ == 'pearsonr':
                        sim, tail = similarity([items[i][k] for k in common_keys], [items[ii][k] for k in common_keys])
                    elif similarity.__name__ == 'jaccard_similarity_score':
                        sim = similarity([items[i][k] for k in common_keys], [items[ii][k] for k in common_keys])

                    if not isnan(sim):
                        try:
                            similarities[i].append((ii, sim))
                        except KeyError:
                            similarities.setdefault(i, [])
                            similarities[i].append((ii, sim))
        similarities[i].sort(key=lambda tup: tup[1], reverse=True)

    dump(similarities, open("similarities_itembased1.p", "wb"))
    e3 = default_timer()
    # print "Similarities exec time", (e3 - s3) / 60, "min"

    s4 = default_timer()
    for i in items:
        stats.append((i, sum([items[i][q] for q in items[i]])))

    stats.sort(key=lambda tup: tup[1], reverse=True)
    dump(stats, open("stats_itembased1.p", "wb"))
    e4 = default_timer()
    # print "Stats exec time", (e4 - s4) / 60, "min"

    end = default_timer()
    # print "Execution time data.py", (end - start) / 60, "min"