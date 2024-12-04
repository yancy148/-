from flask import Flask, render_template, request, redirect, url_for, flash, session
import pydicom
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个密钥用于会话管理

# 模拟数据库，存储患者信息和对应的 DICOM 文件路径
patients = {
    'yanxu': {
        'password': '123456',
        'dcm_data': [
            {'path': '素材/image-000001.dcm', 'study_date': '20230101'},
            {'path': '素材/image-000002.dcm', 'study_date': '20230102'},
            {'path': '素材/image-000003.dcm', 'study_date': '20230103'},
            {'path': '素材/image-000004.dcm', 'study_date': '20230104'}
        ]
    },
    'jinyuyang': {
        'password': '123456',
        'dcm_data': []
    }
}


def convert_dcm_to_base64(dcm_path):
    ds = pydicom.dcmread(dcm_path)
    image = ds.pixel_array

    # 将图像数据转换为 PNG 格式并编码为 base64
    buf = io.BytesIO()
    plt.imshow(image, cmap=plt.cm.gray)
    plt.title(f"Patient: {ds.PatientName}, Study Date: {ds.StudyDate}")
    plt.axis('off')  # 隐藏坐标轴
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64, ds.PatientName, ds.StudyDate


@app.route('/')
def home():
    return render_template('Home.html')


@app.route('/登录界面', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in patients and patients[username]['password'] == password:
            session['logged_in'] = True
            return redirect(url_for('patient_image'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('登录界面.html')


@app.route('/患者图像', methods=['GET'])
def patient_image():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    patient_id = 'yanxu'  # 假设我们只处理一个患者
    dcm_data = patients[patient_id]['dcm_data']

    # 获取用户选择的日期
    selected_date = request.args.get('study_date')

    # 如果选择了日期，则过滤图像
    if selected_date:
        images = []
        for item in dcm_data:
            if item['study_date'] == selected_date:
                img_base64, patient_name, study_date = convert_dcm_to_base64(item['path'])
                images.append({
                    'img_base64': img_base64,
                    'patient_name': patient_name,
                    'study_date': study_date
                })
    else:
        # 如果没有选择日期，则显示所有图像
        images = [
            {
                'img_base64': img_base64,
                'patient_name': patient_name,
                'study_date': study_date
            }
            for item in dcm_data
            for img_base64, patient_name, study_date in [convert_dcm_to_base64(item['path'])]
        ]

    return render_template('患者图像.html', images=images)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/医院信息')
def hospital_info():
    # 这里可以添加医院信息的具体内容
    return render_template('医院信息.html')


if __name__ == '__main__':
    app.run(debug=True)