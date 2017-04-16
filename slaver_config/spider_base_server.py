# coding=utf-8
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import os
import zipfile

app = Flask(__name__)
# file_dir = '/Users/gaoliang/Desktop'
file_dir = "/app/spider_cli/spiders"  # 实际部署时使用的文件夹
app.config['UPLOAD_FOLDER'] = file_dir
ALLOWED_EXTENSIONS = {'zip'}

config_dir = '/etc/supervisor/conf.d/'

scrapy_conf_templates = """[program:{0}]
directory=/app/spider_cli/spiders/{0}
command=scrapy crawl {0}
stdout_logfile=/var/log/supervisor/{0}_stdout.log
redirect_stderr=true
autostart=false
"""
portia_conf_tempaltes = """
[program:{0}]
directory=/app/spider_cli/spiders
command=portiacrawl {0} {0}
stdout_logfile=/var/log/supervisor/{0}_stdout.log
redirect_stderr=true
autostart=false
"""


def create_conf(spider_name, spider_type):
    file_path = os.path.join(config_dir, spider_name + ".conf")
    with open(file_path, "w") as f:
        if spider_type == "scrapy":
            f.write(scrapy_conf_templates.format(spider_name))
        elif spider_type == "portia":
            f.write(portia_conf_tempaltes.format(spider_name))


def un_zip(file_name):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(file_name.split(".")[0]):
        pass
    else:
        os.mkdir(file_name.split(".")[0])
    for names in zip_file.namelist():
        zip_file.extract(names, file_name.split(".")[0])
    zip_file.close()


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传
@app.route('/test/upload')
def upload_test():
    return render_template('upload.html')


# 上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
    spider_type = request.form['type']
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        filename = secure_filename(f.filename)
        create_conf(filename.split('.')[0], spider_type)
        f.save(os.path.join(file_dir, filename))  # 保存文件到upload目录
        un_zip(os.path.join(file_dir, filename))
        os.system("supervisorctl update")
        return jsonify({"success": True, "errmsg": ""})
    else:
        return jsonify({"success": False, "errmsg": "上传失败"})


# 上传文件
@app.route('/api/delete', methods=['POST'], strict_slashes=False)
def delete():
    name = request.form['name']
    try:
        os.remove(os.path.join(config_dir, name + '.conf'))
        os.system("supervisorctl update")
        return jsonify({"success": True})
    except:
        return jsonify({'success': False})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
