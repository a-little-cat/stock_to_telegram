import requests
from apscheduler.schedulers.blocking import BlockingScheduler

token = '123:123456789'
chatId = '123'


def value_get(code):
    r1 = requests.get("http://hq.sinajs.cn/list=s_sh%s" % (code,))
    r2 = requests.get("http://hq.sinajs.cn/list=s_sz%s" % (code,))
    r = r1 if len(r1.text) > len(r2.text) else r2

    res = r.text.split(',')
    if len(res) > 1:
        return res[0][23:], float(res[2])
    return u'——无——',  10000


money_store = 0


def get_price():
    data = []
    with open("chicang.info") as f:
        for line in f.readlines():
            comment, code, num, price = line.split()
            info = {'comment': comment, 'code': code,
                    'num': int(num), 'price': float(price)}
            data.append(info)

    money = 0
    reply_text = ''
    for info in data:
        name, price = value_get(info['code'])
        if(price == 10000):
            print("didn't found code")
            continue
        info['name'] = name
        info['price'] = price
        info['money'] = price * info['num']

    data = sorted(data, key=lambda i: i['money'], reverse=True)

    for info in data:
        reply_text += f"{info['name']} {info['num']:5d} {info['price']:+4.2f} {int(info['price'] * info['num']):+5d}\n"
        money += info['price'] * info['num']

    reply_text += f"today : {money}"
    return money, reply_text


def stock_job():
    global money_store
    money_now, reply_text = get_price()
    if(abs(money_store-money_now) > 100):
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatId}&text={reply_text}"
        requests.get(url)
    money_store = money_now


scheduler = BlockingScheduler()
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=9, minute='30-59')
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=10, minute='0-59')
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=11, minute='0-30')
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=13, minute='30-59')
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=14, minute='0-59')
scheduler.add_job(stock_job, 'cron', day_of_week='mon-fri',
                  hour=15, minute='0-30')

scheduler.start()
