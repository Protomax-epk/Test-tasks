import requests
import os
import time
import string as strx
import json


def get_data():
    print('parsing ')
    tasks_url = 'https://json.medrating.org/todos'
    users_url = 'https://json.medrating.org/users'
    tasks = json.loads(requests.get(tasks_url).text)
    users = json.loads(requests.get(users_url).text)

    return tasks, users


def dir_maker(dirname = 'tasks'):
    print(f'creating {dirname} directory')
    path = os.getcwd()
    try:
        os.mkdir(os.path.join(path, dirname))
    except FileExistsError:
        print('dir already exists, skipping')
    dir_path = f'{path}/{dirname}'
    return dir_path

def report_maker(tasks, users, dir_path):
    report_template = strx.Template('Отчёт для ${company_name}.'
                                    '\n$full_name <${email}> $date $time'
                                    '\nВсего задач: $tasks'
                                    '\n'
                                    '\nЗавершённые задачи (${finished_tasks}):'
                                    '\n$fin_task_text'
                                    '\n'
                                    '\nОставшиеся задачи (${remain_tasks}):'
                                    '\n$rem_task_text')
    users_tasks_amount = {}
    finished_tasks_amount = {}
    finished_tasks = {}
    remaining_tasks_amount = {} #Можно завернуть как лист из двух словарей для лаконичности
    remaining_tasks = {}
    for task in tasks:
        try:
            if task['completed']:
                try:
                    users_tasks_amount[task['userId']] += 1
                except KeyError:
                    users_tasks_amount[task['userId']] = 1

            if task['completed'] == True:
                try:
                    finished_tasks_amount[task['userId']] += 1
                except KeyError:
                    finished_tasks_amount[task['userId']] = 1
                try:
                    finished_tasks[task['userId']].append(f"{task['title']}")
                except KeyError:
                    finished_tasks[task['userId']] = [f"{task['title']}"]

            else:
                try:
                    remaining_tasks_amount[task['userId']] += 1
                except KeyError:
                    remaining_tasks_amount[task['userId']] = 1
                try:
                    remaining_tasks[task['userId']].append(f"{task['title']}")
                except KeyError:
                    remaining_tasks[task['userId']] = [f"{task['title']}"]
        except KeyError:
            pass

    for user in users:
        values = {'company_name': user['company']['name'],
                  'full_name': user['name'],
                  'email': user['email'],
                  'date': time.strftime('%d.%m.%Y',time.localtime()),
                  'time': time.strftime('%H:%M',time.localtime()),
                  'tasks': '',
                  'finished_tasks': '',
                  'fin_task_text': '',
                  'remain_tasks': '',
                  'rem_task_text': ''}
        try:
            values['tasks'] = users_tasks_amount[user['id']]
        except KeyError:
            values['tasks'] = 0
        try:
            values['finished_tasks'] = finished_tasks_amount[user['id']]
        except KeyError:
            values['finished_tasks'] = 0
        try:
            values['remain_tasks'] = remaining_tasks_amount[user['id']]
        except KeyError:
            values['remain_tasks'] = 0
        for task_title in finished_tasks[user['id']]:
            if len(task_title) > 48:
                values['fin_task_text'] += f'{task_title[:48]}...\n'
            else:
                values['fin_task_text'] += f'{task_title}\n'
        for task_title in remaining_tasks[user['id']]:
            if len(task_title) > 48:
                values['rem_task_text'] += f'{task_title[:48]}...\n'
            else:
                values['rem_task_text'] += f'{task_title}\n'

        path = f'{dir_path}/{user["username"]}.txt'

        try:

            with open(path,mode= 'x', encoding='utf-8') as report:
                            report.writelines(report_template.substitute(values))
        except FileExistsError:
            time_of_creation = time.strftime("%Y-%m-%dT%H:%M", time.localtime(os.path.getctime(path)))
            print(time_of_creation)
            old_report_path = f'{dir_path}/old_{user["username"]}_{time_of_creation}'+'.txt'
            with open(path,mode= 'r', encoding='utf-8') as old_report:
                with open(old_report_path,mode= 'w', encoding='utf-8') as report_copy:
                    report_copy.writelines(old_report.readlines())
            with open(path,mode= 'w', encoding='utf-8') as report:
                report.writelines(report_template.substitute(values))






def main():
    tasks, users = get_data()
    dir_path = dir_maker()
    report_maker(tasks, users, dir_path)


if name == 'main':
    main()