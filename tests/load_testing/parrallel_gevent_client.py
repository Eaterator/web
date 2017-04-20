from gevent import monkey
monkey.patch_all()

import requests
import statistics
import json
from collections import defaultdict
from gevent.pool import Pool
from random import seed, sample, randint
from time import time

seed(40)

USERNAME = 'msalii@ukr.net'
PASSWORD = 'mSalii123!'
INGREDIENTS = ["chicken", "rice", "bean", "salmon", "egg", "rice", "celery", "carrot", "pepper", "beef", "pork",
               "beef", "pork", "onion", "cheese", "salt", "pepper"]
TIMES = defaultdict(lambda: [])
FAILED_REQUESTS = defaultdict(lambda: 0)
TOTAL_REQUESTS = 0
# 2500 makes this baby run hot! maybe stay with 1000 with no cache!!
REQUEST_NUM = 2000
# TAILING_NUM = [1000, 750, 500, 100]
# TAILING_NUM = [t if t < REQUEST_NUM else REQUEST_NUM for t in TAILING_NUM]
PARALLEL_REQUESTS = 1


def submit_search(jwt_token):
    global TOTAL_REQUESTS
    token = jwt_token
    ingredients = sample(INGREDIENTS, randint(1, 5))
    search_payload = json.dumps({"ingredients": ingredients})
    start = time()
    resp = requests.post('http://localhost:5000/recipe/v2/search',
                         data=search_payload,
                         headers={
                             "Authorization": "Bearer {0}".format(token),
                             "Content-Type": "application/json"
                         })
    TIMES[len(ingredients)].append(time() - start)
    TOTAL_REQUESTS += 1
    if resp.status_code != 200:
        global FAILED_REQUESTS
        FAILED_REQUESTS[len(ingredients)] += 1
    return


# def test_auth(_):
#     resp = requests.post('http://localhost:5000/auth/',
#                          data=json.dumps({"username": USERNAME, "password": PASSWORD}),
#                          headers={"Content-Type": "application/json"})
#     TIMES.append(time() - start)
#     if resp.status_code != 200:
#         global FAILED_REQUESTS
#         FAILED_REQUESTS += 1
#     return


def get_authorization():
    resp = requests.post('http://localhost:5000/auth/',
                         data=json.dumps({"username": USERNAME, "password": PASSWORD}),
                         headers={"Content-Type": "application/json"})
    return resp.json()['access_token']


if __name__ == '__main__':
    jwt_token = get_authorization()
    pool = Pool(PARALLEL_REQUESTS)
    start = time()
    pool.map(submit_search, [jwt_token]*REQUEST_NUM)
    # pool.map(test_auth, [jwt_token]*REQUEST_NUM)

    print('\n\n--------------------Summary--------------------------')
    print("Total Requests: \t\t{0}".format(REQUEST_NUM))
    print("Concurrent requests: \t\t{0}".format(PARALLEL_REQUESTS))
    print("Total time: \t\t{0:.2f} s".format(time() - start))
    print("Average req/s: \t\t{0}".format(TOTAL_REQUESTS / (time() - start)))

    print('\nResponse Data:')
    for key, item in TIMES.items():
        print('\t Searches of length: {0}'.format(key))
        print('\t\tAverage response time: \t{0} s'.format(statistics.mean(item)))
        print('\t\tStandard deviation: \t{0} s'.format(statistics.pstdev(item)))
        print("\t\tMaximum response time: \t{0} s".format(max(item)))
        print("\t\tMinimum response time: \t{0} s".format(min(item)))
        print("\t\tTotal requests failed: \t{0}".format(FAILED_REQUESTS[key]))
        print("\t\tPercent Failed:\t{0:.2f} %".format(FAILED_REQUESTS[key]/len(item)*100))

    # for tail_num in TAILING_NUM:
    #     print('\n\nTailing Responses {0}: '.format(tail_num))
    #     print('\tAverage response time: \t{0} s'.format(statistics.mean(TIMES[tail_num:])))
    #     print('\tStandard deviation: \t{0} s'.format(statistics.pstdev(TIMES[tail_num:])))
    #     print("\tMaximum response time: \t{0} s".format(max(TIMES[tail_num:])))
    #     print("\tMinimum response time: \t{0} s".format(min(TIMES[tail_num:])))
    #     print("\tTotal requests failed: \t{0}".format(FAILED_REQUESTS))
    #     print("\tPercent Failed: \t{0:.2f} %".format(FAILED_REQUESTS / len(TIMES[tail_num:]) * 100))

    print('-----------------------------------------------------\n\n')
