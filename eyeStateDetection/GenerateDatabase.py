import datetime
import random
import csv

max_variation = 0.05
n = random.randint(1, 25)
curDate = datetime.datetime.now() - datetime.timedelta(days=300)
resultDict = []
details = ["datetime", "program", "perclos", "fatigue", "person", "bpm"]
rows = [[0, 0, 0.4, 0.2, 0, 0]]
possibleApplications = ["Visual Studio Code", "Visual Studio", "Google Chrome", "Outlook", "Teams"]
while curDate < datetime.datetime.now():
    #most mondays should bring more fatigue so script should reflect this
    #fatigue throught the day should increase

    first = curDate

    last_fatigue = rows[-1][3]
    if last_fatigue is None:
        last_fatigue = 0.4

    last_perclos = rows[-1][2]
    if last_perclos is None:
        last_perclos = 0.4

    third = random.uniform(last_perclos - max_variation, last_perclos + max_variation)

    if third > 1.0:
        third = 1

    if third < 0:
        third = 0.1

    fourth = third * random.random()
    if third > 0.8:
        fourth = random.uniform(third - max_variation*1.35, third + max_variation)
    if 0.6 < third < 0.8:
        fourth = random.uniform(third - max_variation*1.15, third + max_variation)
    if 0.4 < third < 0.6:
        fourth = random.uniform(third - max_variation, third + max_variation*0.85)
    if third < 0.4:
        fourth = random.uniform(third - max_variation, third + max_variation*0.65)

    if fourth > 1.0:
        fourth = 1

    if fourth < 0:
        fourth = 0.1

    fith = random.randint(80, 100)
    if fourth > 0.75:
        fith = random.randint(40, 50)
    if 0.75 > fourth > 0.50:
        fith = random.randint(55, 65)


    secondChance = third
    second = possibleApplications[-1]
    if secondChance < 0.1:
        second = possibleApplications[0]
    if 0.1 <= secondChance < 0.45:
        second = possibleApplications[1]
    if 0.45 <= secondChance < 0.55:
        second = possibleApplications[2]
    if 0.55 <= secondChance < 0.85:
        second = possibleApplications[3]

    if curDate.weekday() == 1:
        if third < 0.5:
            third * 1.75
    rows.append([first, second, third, fourth, "personA", fith])

    curDate = curDate + datetime.timedelta(minutes=1)
    if curDate.time().hour > 18:
        curDate = curDate + datetime.timedelta(days=1)
        curDate = curDate - datetime.timedelta(hours=9)

with open('fatigueDataset.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(details)
    write.writerows(rows[1:])
