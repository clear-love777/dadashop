from django.core.mail import send_mail

from ny3.celery import app


@app.task
def send_active_email(email,active_url):
    #发送激活邮件
    try:
        subject="达达商城激活邮件"
        html_message="""
        <p>尊敬的用户 您好</p>
        <p>激活链接为<a href="%s" target="blank">点击激活</a></p>
        """%active_url
        send_mail(subject=subject,html_message=html_message,
                  from_email="490159632@qq.com",recipient_list=[email],message="")
        print("----send mail ok")
    except Exception as e:
        print("--send email error")
        print(e)