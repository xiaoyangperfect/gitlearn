# -*- coding: utf-8 -*-
import os
from flask import Flask, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import object_detect
import detection_util
import time
import json

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'JPG'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd() + "/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

version = 1.0
content = ''

class DetectResult():
    def __init__(self, isSuccess, data, errorMessage):
        self.isSuccess = isSuccess
        self.data = data
        self.errorMessage = errorMessage

    def __repr__(self):
        return repr(self.isSuccess, self.data, self.errorMessage)

class DetectResults():
    def __init__(self, isSuccess, detectResult, errorMessage):
        self.isSuccess = isSuccess
        self.detectResult = detectResult
        self.errorMessage = errorMessage

    def __repr__(self):
        return repr(self.isSuccess, self.data, self.errorMessage)

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=text name=valid_area>
         <input type=submit value=上传>
    </form>
    '''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/upload', methods=['GET', 'POST'])
def uploaded():
    try:
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                valid_area = request.values.get('valid_area')
                detect_result = object_detect.detection(file_path, valid_area)
                detect_result = json.dumps(DetectResult(True, detect_result, "").__dict__)
                delet_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return detect_result
            else:
                return json.dumps(DetectResult(False, None, "File name is not allowed").__dict__)
        else:
            return json.dumps(DetectResult(False, None, "GET method is not supported").__dict__)
    except Exception as e:
        return json.dumps(DetectResult(False, None, str(e)).__dict__)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # try:
        if request.method == 'POST':
            time1 = time.time()
            print(str(time1))
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_url = url_for('uploaded_file', filename=filename)
                valid_area = request.form.get('valid_area')
                print(valid_area)
                # detect_result = object_detect.detectionV2_save_tamp_image(file_path)
                detect_result = detection_util.run(file_path)
                detect_result = json.dumps(DetectResults(True, detect_result, "").__dict__)
                delet_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print(str(time.time()))
                time2 = str(time.time() - time1)
                return html + '<br><img src=' + file_url + '>' + '--------------' + detect_result + '.....' + time2
            else:
                return json.dumps(DetectResult(False, None, "File name is not allowed").__dict__)
        else:
            return html
    # except Exception as e:
    #     return json.dumps(DetectResult(False, None, str(e)).__dict__)


def delet_files():
    filelist = []
    rootdir = app.config['UPLOAD_FOLDER']
    filelist = os.listdir(rootdir)
    for f in filelist:
        filepath = os.path.join(rootdir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)


def delet_file(filename):
    rootdir = app.config['UPLOAD_FOLDER']
    path = os.path.join(rootdir, filename)
    if os.path.isfile(path):
        os.remove(path)

@app.route('/download/<filename>')
def download(filename):
    path = os.getcwd() + "/temp_image/"
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/download/')
def index():
    return showHtml()

@app.route('/announce_input/', methods=['GET', 'POST'])
def announce_input():
    if request.method == 'POST':
        global version
        global content
        version = request.form.get('version')
        content = request.form.get('content')
        return announceHtml() + '<textarea type=text>发布成功</textarea>'
    else:
        return announceHtml()

@app.route('/announce/')
def announce():
    res = '{ "version":' + str(version) + ', "content":' + content + '}'
    return res

def announceHtml():
    html = '''
    <title>Announce</title>
    <form method=post enctype=multipart/form-data>
         <textarea type=text name=version> Version
    '''
    s2 = '''</textarea>
        <br text="version">
         "version"
         <input type=text name=version>
         </br>
         <br text="content">
         "content"
         <input type=text name=content>
         </br>
         <input type=submit value=发布>
    </form>
    '''
    return html + str(version) + s2

def showHtml():
    html_str = '''
    <!DOCTYPE html>
    <title>Download File</title>
    <h1>图片集下载</h1>
    <ul>
    '''
    files = os.listdir(os.getcwd() + '/temp_image/')
    click = ''
    for file in files:
        if os.path.basename(file).endswith('.zip'):
            click = click + '<li> <a href="/download/' + os.path.basename(file) + '"> ' + os.path.basename(file) + '</a></li>'
    html_str = html_str + click + '</ul>'
    return html_str


def run():
    app.run()


if __name__ == '__main__':
    app.run()
