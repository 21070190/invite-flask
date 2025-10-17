from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

app = Flask(__name__)

# Thư mục lưu ảnh tạm & kết quả
UPLOAD_FOLDER = os.path.join('static', 'uploads')
CARD_FOLDER = os.path.join('static', 'cards')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARD_FOLDER, exist_ok=True)

# Font & nền
FONT_PATH = os.path.join('static', 'fonts', 'Roboto_Condensed-Regular.ttf')
BASE_CARD_PATH = os.path.join('static', 'invite_bg.jpg')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_card', methods=['POST'])
def create_card():
    name = request.form.get('name', 'Bạn')
    uploaded_file = request.files.get('image')

    # Mở ảnh nền
    base_card = Image.open(BASE_CARD_PATH).convert('RGBA')

    # Nếu người dùng upload ảnh thì dán vào thiệp
    if uploaded_file and uploaded_file.filename != '':
        img_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(img_path)

        user_img = Image.open(img_path).convert('RGBA')
        user_img = user_img.resize((200, 200))

        # Dán ảnh lên nền
        base_card.paste(user_img, (150, 150), user_img)

    # Viết chữ
    draw = ImageDraw.Draw(base_card)
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except:
        font = ImageFont.load_default()

    text = f"Chúc {name} một ngày thật vui vẻ!"
    draw.text((100, 400), text, font=font, fill=(255, 105, 180))

    # Lưu thiệp kết quả
    output_filename = f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_path = os.path.join(CARD_FOLDER, output_filename)
    base_card.save(output_path)

    # Hiển thị kết quả (chưa tải)
    return render_template('result.html', card_filename=output_filename, name=name)

@app.route('/download/<filename>')
def download_card(filename):
    return send_from_directory(CARD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
