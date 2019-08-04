from collections import defaultdict

def groupby_subject(timetable):
    groupby = defaultdict(list)
    for _class in timetable:
        groupby[_class["subject_code"]].append(_class)
    return groupby