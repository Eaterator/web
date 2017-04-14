from gevent import monkey
monkey.patch_all()

import requests
import statistics
import json
from gevent.pool import Pool
from random import seed, sample, randint
from time import time

seed(40)

USERNAME = 'msalii@ukr.net'
PASSWORD = 'mSalii123!'
INGREDIENTS = ["chicken", "rice", "bean", "salmon", "egg", "rice", "celery", "carrot", "pepper", "beef", "pork"]
TIMES = []
FAILED_REQUESTS = 0
# 2500 makes this baby run hot! maybe stay with 1000 with no cache!!
REQUEST_NUM = 5000
TAILING_NUM = [1000, 750, 500, 100]
TAILING_NUM = [t if t < REQUEST_NUM else REQUEST_NUM for t in TAILING_NUM]
PARALLEL_REQUESTS = 100


def submit_search(jwt_token):
    token = jwt_token
    search_payload = json.dumps({"ingredients": sample(INGREDIENTS, randint(1, 3))})
    start = time()
    resp = requests.post('http://localhost:5000/recipe/v2/search',
                         data=search_payload,
                         headers={
                             "Authorization": "Bearer {0}".format(token),
                             "Content-Type": "application/json"
                         })
    TIMES.append(time() - start)
    if resp.status_code != 200:
        global FAILED_REQUESTS
        FAILED_REQUESTS += 1
    return


def test_auth(_):
    resp = requests.post('http://localhost:5000/auth/',
                         data=json.dumps({"username": USERNAME, "password": PASSWORD}),
                         headers={"Content-Type": "application/json"})
    TIMES.append(time() - start)
    if resp.status_code != 200:
        global FAILED_REQUESTS
        FAILED_REQUESTS += 1
    return


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
    print("Total Requests: \t{0}".format(REQUEST_NUM))
    print("Concurrent requests: \t{0}".format(PARALLEL_REQUESTS))
    print("Total time: \t{0:.2f} s".format(time() - start))

    print('\nResponse Data:')
    print('\tAverage response time: \t{0} s'.format(statistics.mean(TIMES)))
    print('\tStandard deviation: \t{0} s'.format(statistics.pstdev(TIMES)))
    print("\tMaximum response time: \t{0} s".format(max(TIMES)))
    print("\tMinimum response time: \t{0} s".format(min(TIMES)))
    print("\tTotal requests failed: \t{0}".format(FAILED_REQUESTS))
    print("\tPercent Failed:\t{0:.2f} %".format(FAILED_REQUESTS/len(TIMES)*100))

    for tail_num in TAILING_NUM:
        print('\n\nTailing Responses {0}: '.format(tail_num))
        print('\tAverage response time: \t{0} s'.format(statistics.mean(TIMES[tail_num:])))
        print('\tStandard deviation: \t{0} s'.format(statistics.pstdev(TIMES[tail_num:])))
        print("\tMaximum response time: \t{0} s".format(max(TIMES[tail_num:])))
        print("\tMinimum response time: \t{0} s".format(min(TIMES[tail_num:])))
        print("\tTotal requests failed: \t{0}".format(FAILED_REQUESTS))
        print("\tPercent Failed: \t{0:.2f} %".format(FAILED_REQUESTS / len(TIMES[tail_num:]) * 100))

    print('-----------------------------------------------------\n\n')
