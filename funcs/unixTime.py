from datetime import datetime, timezone, timedelta
    
def datetimeToString(time):
    time = int(time)

    try: return str(datetime.fromtimestamp(time))
    except: return str(datetime.fromtimestamp(time/1000))

def datetimeEdit(dates, times, utf=0):
    for i in range(len(dates)): dates[i] = int(dates[i])
    for i in range(len(times)): times[i] = int(times[i])
    
    if times[1] >= 59:
        times[0] += 1
        times[1] = 0
    
    return str(datetime(
        dates[0],
        dates[1],
        dates[2],
        times[0],
        times[1],
        times[2]
    ) + timedelta(hours=utf))