## 功能

1. 博客和评论支持基本markdown语法（不支持图片）。
2. 允许「一般用户」用邮箱注册、登录、修改登录邮箱、修改登录密码，忘记密码重置，修改个人信息（姓名、位置、关于我）。
3. 允许「管理员」可以修改、任何人的评论、博客。
4. 用户头像和[Gravatar](https://en.gravatar.com/)通过邮箱自动关联。
5. 未注册用户只有阅读权限。

## 环境变量

* MINIBLOG_ADMIN: 管理员电子邮箱地址
* MAIL_USERNAME: 管理员电子邮箱地址
* MAIL_PASSWORD: 管理员电子邮箱登录密码

## 部署脚本

首先保证把改动已经被提交到本地仓库。

初始化生产环境：

```bash
proxychains4 heroku config:set MAIL_USERNAME=$MAIL_USERNAME
proxychains4 heroku config:set MINIBLOG_ADMIN=$MAIL_USERNAME
proxychains4 heroku config:set MAIL_PASSWORD=$MAIL_PASSWORD

proxychains4 git push heroku master
proxychains4 heroku run python manage.py reset_db

proxychains4 heroku restart
```

之后如果对程序有改动，部署步骤为：

```bash
proxychains4 git push heroku master
proxychains4 heroku run python manage.py db migrate
proxychains4 heroku run python manage.py db upgrade
proxychains4 heroku restart
```
