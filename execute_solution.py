# -*- coding: utf-8 -*-

import requests, time, pyprog, json

token = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'
url = "https://api.vk.com/method/execute?"
params_const = {
        'access_token': token,
        'code': '',
        'v': '5.92'
    }

def get_friends(user_id):
    code = '''
    var user_id = %s;
    var res = API.friends.get({"user_id": user_id}).items;
    return res;
    ''' % user_id
    params = params_const
    params['code'] = code
    response = requests.get(url, params)
    friends = response.json()['response']
    return friends


def is_legacy_user():
    friends = get_friends(user_id)
    code = '''
        var user_ids = %s;
        var res = API.users.get({"user_ids": user_ids});
        return res;
        ''' % friends
    params = params_const
    params['code'] = code
    params['fields'] = 'deactivated, blacklisted'
    response = requests.get(url, params)
    result_dict = response.json()
    for item in result_dict['response']:
        if 'deactivated' in item.keys() or ('blacklisted' in item.keys() and item['blacklisted'] != 0):
            result_dict['response'].remove(item)
    leg_friends = [items['id'] for items in result_dict['response']]
    return leg_friends


def get_own_groups(user_id):
    code = '''
    var user_id = %s;
    var res = API.groups.get({"user_id": user_id}).items;
    return res;
    ''' % user_id
    params = params_const
    params['code'] = code
    response = requests.get(url, params)
    own_groups = response.json()['response']
    return own_groups


def is_group_member():
    own_groups = get_own_groups(user_id)
    friends = is_legacy_user()
    print('Найдено ' + str(len(own_groups)) + ' групп')
    gr_list = []
    for index, group in enumerate(own_groups):
        prog = pyprog.ProgressBar(' ', '', len(own_groups))
        is_unique = 1
        code = '''
        var group_id = %s;
        var user_ids = %s;
        var response = API.groups.isMember({"user_ids": user_ids, "group_id": group_id});
        return response;
        ''' % (group, friends)
        params = params_const
        params['code'] = code
        while 1:
            try:
                response = requests.get(url, params)
                time.sleep(0.3)
            except Exception:
                print('Too many requests per second, waiting ...')
                continue
            prog.set_stat(index + 1)
            prog.update()
            break

        for res in response.json()['response']:
            if res['member'] > 0:
                is_unique = 0
        if is_unique == 1:
            gr_list.append(group)

    return gr_list


def get_result():
    print('Ищем ...')
    groups = is_group_member()
    print('\nПолучение результата ...\n')
    prog = pyprog.ProgressBar(' ', '', len(groups))
    result = []
    for index, res_group in enumerate(groups):
        code = '''
            var group_id = %s;
            var response = API.groups.getById({"group_id": group_id});
            return response;
            ''' % res_group
        params = params_const
        params['code'] = code
        params['extended'] = 1
        params['fields'] = 'members_count'
        while 1:
            try:
                response = requests.get(url, params)
                time.sleep(0.2)
            except Exception:
                print('Too many requests per second, waiting ...')
                continue
            result.append(response.json()['response'][0])
            prog.set_stat(index + 1)
            prog.update()
            break
    with open('result.json', 'a') as file:
        json.dump(result, file, indent=4, ensure_ascii=True)
    print('\nРезультат сохранен в файл result.json в текущей директории')


if __name__ == '__main__':
    user_id = 171691064
    get_result()
