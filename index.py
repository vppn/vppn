# encoding: utf-8
'''
Created on Jan 8, 2014

@author: vppn
@contact: vppn.us@gmail.com
@license: Apache License, Version 2.0 http://www.apache.org/licenses/LICENSE-2.0
@version: 0.1
'''

import MySQLdb
import json
import os
import re
from mod_python import apache

index_html='''<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>vppn trial</title>
<script src="//code.jquery.com/jquery-1.11.1.min.js"></script>
<script>
$(function() {
    $('#addUserBtn').click(function( event ) {
        var userid = $("#newuserid").val();
        if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(userid)){
            alert('invalid email\\n邮件格式不对\\n無効な電子メール');
        }else{
            $('#addUserBtn').removeClass().addClass('btn btn-info btn-xs').html('adding...');
            $.getJSON("./index/trial",{"userid":userid}, function( data ) {
                switch(data.resultCode){
                    case 0:
                        $('#addUserBtn').html('<span class="glyphicon glyphicon-send"></span> ' + data.message)
                        .removeClass('btn-info').addClass('btn btn-success btn-xs').off('click');
                    break
                    case 1:
                        $('#addUserBtn').html('<span class="glyphicon glyphicon-flash"></span> ' + data.message)
                        removeClass('btn-info').addClass('btn btn-danger btn-xs');
                    break;
                }
            });
        }
    });
});
</script>
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">

<!-- Optional theme -->
<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">

<!-- Latest compiled and minified JavaScript -->
<script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container">
<h3>vppn trial 自助试用 ビュッフェ試用</h3>
<p>
<div id='newuserarea'>
<p><input id='newuserid' type='email' class='form-control' placeholder='Email' data-container="body" data-toggle="popover" data-placement="bottom" data-content="Vivamus
sagittis lacus vel augue laoreet rutrum faucibus." /></p>
</div>
<button id='addUserBtn' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-envelope'></span> trial 試用</button>
<a href='http://www.baidu.com/#wd=vpn%20pptp%E8%AE%BE%E7%BD%AE&rsv_bp=0&tn=baidu&rsv_spt=3&ie=utf-8&rsv_sug3=8&rsv_sug4=739&rsv_sug1=7&oq=vpn%20pptp&rsv_sug2=0&f=3&rsp=0&inputT=7774' target='_blank'>setting 設置</a><br>
</div>
</body>
</html>
'''
def index(req):
    return index_html
def trial(req,userid):
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", userid):
        req.write(json.dumps({"resultCode":1,"message": ("invalid email\n邮件格式不对\n無効な電子メール")}))
        return
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='vppn', port=3306)
        cur = conn.cursor()
        cur.execute("select userid,blocked from vppn where userid = %s", userid)
        row = cur.fetchone()
        password = genPassword()
        req.content_type = 'text/plain'
        req.add_common_vars()
        if row:
            if not row[1]:
                cur.execute("UPDATE vppn set password=%s,expired = now(),trialCount = trialCount + 1,updatedate=now() WHERE userid = %s",(password,userid))#req.subprocess_env['REMOTE_ADDR'],userid)
            else:
                return
        else:
            cur.execute("insert into vppn (userid,password,expired,trialCount,memo,createdate,updatedate) value (%s,%s,now(),1,'trialUser',now(),now()) ",(userid,password))
        cur.execute("select expired from vppn where userid = %s", userid)
        expired = cur.fetchone()[0]
        cur.close()
        conn.close()
        updateAuth0()
        sendmail(userid,password,expired)
        req.write(json.dumps({"resultCode":0,"message": "check mail,看邮件,メールをチェック"}))
    except MySQLdb.Error, e:
        req.write(json.dumps({"resultCode":1,"message": ("Mysql Error %d: %s" % (e.args[0], e.args[1]))}))
def updateAuth0():
    userfile = file("/etc/ppp/chap-secrets", "w");
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='vppn', port=3306)
        cur = conn.cursor()
        cur.execute("select userid,password,DATE_FORMAT(expired, '%Y-%m-%d') from vppn where expired >= date(now())")
        rows = cur.fetchall()
        for row in rows:
            userfile.write(row[0] + "\tpptpd\t" + row[1] + "\t*\n")
        cur.close()
        conn.close()
        #req.write(json.dumps({"resultCode":0,"message": "update ok!"}))
    except MySQLdb.Error, e:
        req.write(json.dumps({"resultCode":1,"message": "Mysql Error %d: %s" % (e.args[0], e.args[1])}))
        pass
    except Exception, e:
#        req.write(e)
#        raise e
        pass
def genPassword():
    return ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(3)))
def sendmail(userid,password,expired):
    from email.mime.text import MIMEText
    from smtplib import SMTP_SSL
    #from subprocess import Popen, PIPE
    ip=getip()
#如果要p2p下载请断开vpn
#个人vpn，流量有限。
#为了让更多人能享受此服务，请节约带宽，谢谢。
    msg1 = MIMEText(u'''http://vppn.us
This Month's Network Transfer Pool
96% Used 4% Remaining
2883GB Used, 149GB Remaining, 3032GB Quota

剩下的流量自用了。下月再对外公开。

The remaining reserve for personal. Available at next month.

申し訳ございません、残りの部分を自分用になります。来月には　サービスを再開にしますので、ご注意ください。
''', _charset='utf-8')
    msg = MIMEText(u'''http://vppn.us
资源有限，占用过度者进黑名单
＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
VPPN账户信息/The information of your VPPN account/ユーザーアカウント情報
＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

亲爱的用户您好：
感谢使用我们的服务！

服务器: %s
您此次的用户名：%s
密码：%s
使用期限：%s


如遇问题，请与我们联系。vppn.us@gmail.com


＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

Dear friends:
Thank you for choosing us!

  server: %s
  The user name is: %s
  Password: %s
  Expiry date: %s


  If you have any problem, please tell us. vppn.us@gmail.com

＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

お客様：
　商品を購入いただいて、誠にありがとうございました。

　今度の商品情報を以下になります。
　サーバ: %s
　ユーザ名：%s
　パスワード：%s
　期限：%s


　問題ありましたら、お気軽にお问い合わせください。vppn.us@gmail.com
''' % (ip,userid,password, expired,ip,userid,password, expired,ip,userid,password, expired), _charset='utf-8')

    ## The SMTP server details

    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_username = "vppn.us@gmail.com"
    smtp_password = "******"#TODO put you email password to this

    msg["From"] = smtp_username
    msg["To"] = userid
    msg["Subject"] = u"http://vppn.us"
    ## Now we can connect to the server and send the email

    s = SMTP_SSL(smtp_server, smtp_port) # Set up the connection to the SMTP server
    try:
        s.set_debuglevel(True) # It's nice to see what's going on

        s.ehlo() # identify ourselves, prompting server for supported features

        # If we can encrypt this session, do it
        if s.has_extn('STARTTLS'):
            s.starttls()
            s.ehlo() # re-identify ourselves over TLS connection

        s.login(smtp_username, smtp_password) # Login

        # Send the email. Note we have to give sendmail() the message as a string
        # rather than a message object, so we need to do msg.as_string()
        s.sendmail(msg['From'], msg['To'], msg.as_string())

    finally:
        s.quit() # Close the connection
def getip():
    #import socket
    #return socket.gethostbyname(socket.gethostname())
    return 'vppn.us'
