from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

app = Flask(__name__)

# Thư mục lưu ảnh
UPLOAD_FOLDER = 'static/uploads'
CARD_FOLDER = 'static/cards'
FONT_PATH = os.path.join('static', 'Roboto-Regular.ttf')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_card', methods=['POST'])
def create_card():
    # Lấy dữ liệu từ form
    name = request.form.get('name', 'Bạn')
    uploaded_file = request.files.get('image')

    # Nền thiệp gốc
    base_card_path = os.path.join('static', 'base_card.png')
    base_card = Image.open(base_card_path).convert('RGBA')

    # Nếu người dùng upload ảnh thì dán vào thiệp
    if uploaded_file and uploaded_file.filename != '':
        img_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(img_path)

        user_img = Image.open(img_path).convert('RGBA')
        user_img = user_img.resize((200, 200))
        base_card.paste(user_img, (150, 150), user_img)

    # Vẽ chữ chúc mừng
    draw = ImageDraw.Draw(base_card)
    font = ImageFont.truetype(FONT_PATH, 40)
    text = f"Chúc {name} một ngày thật vui vẻ!"
    draw.text((100, 400), text, font=font, fill=(255, 105, 180))

    # Lưu ảnh kết quả
    output_filename = f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_path = os.path.join(CARD_FOLDER, output_filename)
    base_card.save(output_path)

    # Chuyển sang trang kết quả (hiển thị và tải về)
    return render_template('result.html', card_filename=output_filename)

@app.route('/download/<filename>')
def download_card(filename):
    return send_from_directory(CARD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
