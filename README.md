## 环境准备

```
python 3.6.5
MySQL >= 5.6

pip install -r requirement.txt
```

## 运行前需要修改的项

### 修改配置项

```
进入到file文件夹 打开 settings.py 找到
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'file',
        'HOST': '你MySQL的地址',
        'PORT': 你MySQL的端口,
        'USER': '你MySQL的用户名',
        'PASSWORD': '你MySQL的密码',
    }
}
```

### 创建数据库

```
在MySQL中创建file数据库
```

### 在项目根目录下运行

```
python manage.py makemigrations
python manage.py migrate
```

## 运行项目

```
python manage.py runserver 127.0.0.1:8000
```

