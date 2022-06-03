import os
import time
from string import Template
import json
import requests


class User:

    def __init__(self, user,task_dict):
        self.id = user['id']
        self.full_name = user['name']
        self.email = user['email']
        self.username = user['username']
        self.company = user['company']['name']
        self.finish_amount = task_dict['finished']['amount'][user['id']]
        self.remain_amount = task_dict['remaining']['amount'][user['id']]
        self.finish_text = task_dict['finished']['text'][user['id']]
        self.remain_text = task_dict['remaining']['text'][user['id']]


    def create_report(self,dir_name,report_template):
        report_path = os.path.join(os.getcwd(),dir_name, f'{self.username}.txt')
        values = {'company_name': self.company,
                  'full_name': self.full_name,
                  'email': self.email,
                  'date': time.strftime('%d.%m.%Y',time.localtime()),
                  'time': time.strftime('%H:%M',time.localtime()),
                  'tasks': f'{self.finish_amount+self.remain_amount}',
                  'finished_tasks': self.finish_amount,
                  'fin_task_text': self.finish_text,
                  'remain_tasks': self.remain_amount,
                  'rem_task_text': self.remain_text}
        try:
            with open(report_path, mode='x', encoding='utf-8') as report:
                print(f'\nCreating report for {self.username}')
                report.writelines(report_template.substitute(values))
        except FileExistsError:
            time_of_creation = time.strftime("%Y-%m-%dT%H:%M", time.localtime(os.path.getctime(report_path)))
            old_report_path = os.path.join(os.getcwd(), dir_name, f'old_{self.username}_{time_of_creation}.txt')
            with open(report_path, mode='r', encoding='utf-8') as old_report:
                with open(old_report_path, mode='w', encoding='utf-8') as report_copy:
                    print(f'\nCopying old report for {self.username}')
                    report_copy.writelines(old_report.readlines())

            with open(report_path, mode='w', encoding='utf-8') as report:
                print(f'Creating new report for {self.username}')
                report.writelines(report_template.substitute(values))


def dict_fill(state,task_dict,task):
    try:
        task_dict[f'{state}']['amount'][task['userId']] += 1

        if len(task['title']) > 48:
            task_dict[f'{state}']['text'][task['userId']] += task['title'][:48] + '...\n'
        else:
            task_dict[f'{state}']['text'][task['userId']] += task['title'] + '\n'
    except KeyError:
        print(f"Task doesn't have enough info, skipping")

def dict_prepare(state,user_id, task_dict):
    task_dict[f'{state}']['amount'][user_id] = 0
    task_dict[f'{state}']['text'][user_id] = ''

def get_data(task_dict):
    print('\nparsing data from web sources')
    urls = ('https://json.medrating.org/todos', 'https://json.medrating.org/users')
    tasks, users = [requests.get(url).json() for url in urls]

    for user in users:
        dict_prepare('finished', user['id'],task_dict)
        dict_prepare('remaining', user['id'],task_dict)
    for task in tasks:

        try:
            if task['completed']:

                dict_fill('finished',task_dict,task)
            else:
                dict_fill('remaining',task_dict,task)
        except KeyError:
            pass
    return users



def dir_maker(dirname = 'tasks'):
    print(f'\ncreating {dirname} directory')
    try:
        os.mkdir(os.path.join(os.getcwd(), dirname))
    except FileExistsError:
        print(f'\ndir {dirname} already exists, skipping')



def report_maker(dir_name,users,task_dict):
    report_template = Template( 'Отчёт для ${company_name}.'
                                '\n$full_name <${email}> $date $time'
                                '\nВсего задач: $tasks'
                                '\n'
                                '\nЗавершённые задачи (${finished_tasks}):'
                                '\n$fin_task_text'
                                '\n'
                                '\nОставшиеся задачи (${remain_tasks}):'
                                '\n$rem_task_text')

    for user_card in users:
        user_card['username'] = User(user_card,task_dict)
        user_card['username'].create_report(dir_name,report_template)


def main():
    task_dict = {
                 'finished' : {'amount' : {}, 'text' : {}},
                 'remaining' : {'amount' : {},'text' : {}}
                 }
    dir_name = 'tasks'
    users = get_data(task_dict)
    dir_maker(dir_name)
    report_maker(dir_name,users,task_dict)

if __name__ == '__main__':
    main()