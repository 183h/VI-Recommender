from pandas import read_csv
from cPickle import dump, load
from data import prep_data
from timeit import default_timer
from ib_recommender import recommend
from sys import argv
from scipy.stats.stats import pearsonr
from sklearn.metrics import jaccard_similarity_score
from sklearn.metrics.pairwise import cosine_similarity


if __name__ == '__main__':
    start = default_timer()
    print argv[:]
    s_functions = {
        'cosine_similarity': cosine_similarity,
        'pearsonr': pearsonr,
        'jaccard_similarity_score': jaccard_similarity_score
    }

    df_activities = read_csv('vi_assignment2_data_v1/train_activity_v2.csv')
    df_deals = read_csv('vi_assignment2_data_v1/train_deal_details.csv')
    df_items = read_csv('vi_assignment2_data_v1/train_dealitems.csv')

    df_test_users = read_csv('vi_assignment2_data_v1/test_activity_v2.csv')
    users_to_recommend = df_test_users['user_id'].unique()

    prep_data(df_activities, df_deals, df_items, s_functions[argv[1]], int(argv[2]))

    users = load(open('users_itembased.p', 'rb'))
    items = load(open('items_itembased.p', 'rb'))
    similarities = load(open('similarities_itembased.p', 'rb'))
    stats = load(open('stats_itembased.p', 'rb'))
    users_train = df_activities['user_id'].unique()

    recommended = {}

    s1 = default_timer()
    for ur in users_to_recommend:
        date = None
        date = df_test_users[df_test_users['user_id'] == ur].sort_values(['create_time'])['create_time'].iloc[-1]

        recommended[ur] = recommend(ur, date, items, users, df_items, similarities, stats, int(argv[3]))
    e1 = default_timer()
    # print "Recommendation for all users exec time", (e1 - s1) / 60, "min"

    dump(recommended, open("recommended_itembased.p", "wb"))

    # what users bought
    purchases = {}
    for u in df_test_users[['user_id', 'dealitem_id']].itertuples():
            index, u_id, di_id = u
            try:
                purchases[u_id].append(di_id)
            except KeyError:
                purchases.setdefault(u_id, [])
                purchases[u_id].append(di_id)

    hits = 0.0
    for ur in recommended:
        hits += sum([1 for i, r in recommended[ur] if i in purchases[ur]])

    print "Precision", hits / (len(recommended) * 10.0)
    print "Recall", hits / (sum(len(p) for p in purchases.itervalues()) * 1.0)

    end = default_timer()
    # print "Execution time app.py", (end - start) / 60, "min"