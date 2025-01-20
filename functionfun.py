lon = ['matt', 'ben', 'mike', 'mark']
lof = ['happy', 'nervous', 'joyful']

def greeting (listOfNames, listOfFeelings):
    for i in listOfNames:
        for n in listOfFeelings:
            print(i, "feels", n)


greeting(lon, lof)