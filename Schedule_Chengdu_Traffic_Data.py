import time
import schedule
import Chengdu_Traffic_Data_Spider as ctds

def job():
    try:
        spider = ctds.Chengdu_Traffic_Data_Spider()
        spider.run()
        with open ('Log/schedule_log.txt', 'a') as log:
            log.write('Data Collected at ' + time.strftime("%Y-%m-%d %a %H:%M:%S") )
    except:
        with open ('Log/schedule_log.txt', 'a') as log:
            log.write('Error appeared at ' + time.strftime("%Y-%m-%d %a %H:%M:%S") )
        

schedule.every(30).minutes.do(job)
job()

while True:
    schedule.run_pending()
    print('waiting...', end = '\r')
    time.sleep(1)