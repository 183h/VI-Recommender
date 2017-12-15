from cPickle import load
from timeit import default_timer
from pandas import read_csv
from math import isnan


def recommend(user_id, date, items, users, df_items, similarities, stats, neighbours):
    ri = []

    if user_id not in users.keys():
        return stats[10::2][:10]

    for i in df_items[['id']][df_items['coupon_end_time'] > date].itertuples():
        index, i_id = i

        if i_id not in users[user_id]:
            if i_id in similarities:
                if similarities[i_id]:
                    t = [(si, ss, users[user_id][si]) for si, ss in similarities[i_id] if si in users[user_id]]

                    if len(t) >= neighbours:
                    # if t:
                        n = sum([sv[1] * sv[2] for sv in t[:neighbours]])
                        # d = sum([sv[1] for sv in t])
                        r = n

                        if not isnan(r):
                            ri.append((i_id, r))

    ri.sort(key=lambda tup: tup[1], reverse=True)

    if len(ri) < 10:
        d = 10 - len(ri)
        ri = ri + stats[10::2][:d]

    return ri[:10]

if __name__ == '__main__':
    start = default_timer()

    df_activities = read_csv('vi_assignment2_data_v1/train_activity_v2.csv')
    df_deals = read_csv('vi_assignment2_data_v1/train_deal_details.csv')
    df_items = read_csv('vi_assignment2_data_v1/train_dealitems.csv')

    df_test_users = read_csv('vi_assignment2_data_v1/test_activity_v2.csv')
    users_to_recommend = df_test_users['user_id'].unique()

    users = load(open('users_itembased.p', 'rb'))
    items = load(open('items_itembased.p', 'rb'))
    similarities = load(open('similarities_itembased.p', 'rb'))
    stats = load(open('stats_itembased.p', 'rb'))
    users_train = df_activities['user_id'].unique()

    recommended = {}

    for ur in users_to_recommend:
        date = None
        date = df_test_users[df_test_users['user_id'] == ur].sort_values(['create_time'])['create_time'].iloc[-1]

        recommended[ur] = recommend(ur, date, items, users, df_items, similarities, stats)

    end = default_timer()
    print "Execution time ib_recommender.py", (end - start) / 60, "min"