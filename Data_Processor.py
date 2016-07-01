import re
import datetime
import copy
import csv


def parse_commit(line, bug, bugs):
    status = 0
    commit_res = re.search('(commit\s*)(\w*)', line)
    if commit_res:
        commit_hash_code = commit_res.group(2)
        bug['commit'] = commit_hash_code
        bug['source'] = []
        status = 1

    return status


def parse_author(line, bug, bugs):
    status = 0
    author_res = re.search('(Author:\s*)(.*)', line)
    if author_res:
        author = author_res.group(2)
        bug['author'] = author
        status = 2

    return status


def parse_date(line, bug, bugs):
    status = 0
    date_res = re.search('(Date:\s*)(.*)', line)
    if date_res:
        s_date = date_res.group(2)
        s_date = re.sub(r'\s*[+-]([0-9])+', '', s_date)
        date = datetime.datetime.strptime(s_date, '%a %b %d %H:%M:%S %Y')
        bug['date'] = date

        status = 3

    return status


def first_bk_line(line, bug, bugs):
    status = 0
    if line == '\n':
        status = 4

    return status


def parse_bug_id(line, bug, bugs):
    status = 0
    bug['id'] = ''
    bug_id_res = re.search(r'\d{5,6}', line)
    if bug_id_res:
        bug_id = bug_id_res.group()
        bug['id'] = bug_id
        status = 5

    return status


def second_bk_line(line, bug, bugs):
    status = 0
    if line == '\n':
        status = 6

    return status


def parse_source_filename(line, bug, bugs):
    if line == '\n':
        status = 0
        cur_bug = copy.copy(bug)
        bugs.append(cur_bug)
    else:
        source_fn = re.sub(r'\s', '', line)
        bug['source'].append(source_fn)
        status = 6

    return status


def main():
    bugs = []

    status = 0
    nfa = {0: parse_commit, 1: parse_author, 2: parse_date, 3: first_bk_line, 4: parse_bug_id, 5: second_bk_line, 6: parse_source_filename}

    f_log = open('AspectJ_log.txt')
    line = f_log.readline()

    bug = {}

    while line:
        status = nfa.get(status)(line, bug, bugs)
        line = f_log.readline()

    print len(bugs)

    f_log.close()

    csv_file = file('AspectJ-bugs.csv', 'rb')
    reader = csv.reader(csv_file)

    bug_ids = []
    for line in reader:
        if re.search(r'[0-9]+', line[0]):
            bug_ids.append(line[0])

    print len(bug_ids)

    csv_file.close()

    bug_ids = set(bug_ids)

    r_bugs = []
    for b in bugs:
        if b['id'] in bug_ids:
            r_bugs.append(b)

    print len(set([b['id'] for b in r_bugs]))

if __name__ == '__main__':
    main()
