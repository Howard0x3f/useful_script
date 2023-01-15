# -*- coding: utf-8 -*-
import subprocess
import schedule
import time
import os
import shutil
import stat
import smtplib
from email.mime.text import MIMEText
from email.header import Header


targets = ["xxx", "xxx"] #需要克隆的文件夹
last_dates = ["Wed Sep 30 12:00:00 20xx +0800","Wed Sep 30 12:00:00 20xx +0800"]
#设置一个初始时间，格式需要相同，每个目标文件夹都需要设置一个初始时间
dict_dates = dict(zip(targets, last_dates))
clone_time = "00:00"#每天测试的时间
mail_lists = ["xxx@gmail.com","xxx@gmail.com"]#接收通知的邮箱，当代码未更新时只会发通知给第一个邮箱，更新时会通知所有列表中的邮箱。


flag = False #代码是否更新的状态变量

#解决权限问题
def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

#需要配置发送邮件的一些设置
def email(receivers, text, subject):
    mail_server = ""
    mail_port = 25
    sender = ""
    sender_password = ""
    message = MIMEText(text)
    message['From'] = ""
    message['To'] = ','.join(receivers)
    message['Subject'] = subject
    smtp_obj = smtplib.SMTP()
    smtp_obj.connect(mail_server, mail_port)
    smtp_obj.login(sender, sender_password)
    smtp_obj.sendmail(sender, receivers, message.as_string())
    smtp_obj.quit()
    print('-'*20,"email is sended successfully",'-'*20)



# 可以对仓库中的代码执行一些其他操作，例如编译、测试等，需自己补全。
def other_fuc():
    pass


#判断是否更新
def whether_new(targets, mail_lists):
    for target in targets:
        os.chdir('./' + target)
        date = subprocess.getoutput('''git log --pretty=format:"%ad" -1''')
        if(date != dict_dates[target]):
            global flag
            flag = True
            dict_dates[target] = date
        os.chdir('../')
    text = time.strftime('%Y-%m-%d', time.localtime(time.time()))  + '\n'
    if(flag):
        subject = "今日代码存在更新"
        text = text +  "今日代码存在更新\n"
        print('-'*20, "code is new", '-'*20)
        email(mail_lists, subject = subject, text = text )
    else:
        subject = "今日代码未更新"
        text += "今日代码没有更新"
        email([mail_lists[0]], subject, text)
        print('-'*20,"no new code",'-'*20)
    flag = False


#使用git下载
def download_git(targets):
    print("*" * 20, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '*' * 20)
    for target in targets:
        if(os.path.exists(target)):
            shutil.rmtree(target, onerror=readonly_handler)
        git_order = "git clone http://xxx" + target + ".git" #输入需要使用git下载的地址
        print(subprocess.getoutput(git_order))

    print(targets, "clone is finished")




schedule.every().day.at(clone_time).do(download_git, targets = targets)
schedule.every().day.at(clone_time).do(whether_new, targets = targets, mail_lists = mail_lists)
while True:
   schedule.run_pending()
   time.sleep(1)
