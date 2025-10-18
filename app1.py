from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os, base64
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# --- Đường dẫn tuyệt đối ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
CARD_FOLDER = os.path.join(BASE_DIR, 'static', 'cards')
FONT_PATH = os.path.join(BASE_DIR, 'static', 'fonts', 'PLAYFAIRDISPLAY-REGULAR.TTF')
BASE_CARD_PATH = os.path.join(BASE_DIR, 'static', 'invite_bg.png')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


# --- Hàm tạo mask tròn mượt ---
def create_circle_mask(size, upscale=4):
    """Tạo mask tròn mượt bằng supersampling (chống răng cưa)"""
    big_size = (size[0] * upscale, size[1] * upscale)
    mask = Image.new('L', big_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, big_size[0], big_size[1]), fill=255)
    mask = mask.resize(size, Image.Resampling.LANCZOS)
    return mask


@app.route('/create_card', methods=['POST'])
def create_card():
    name = request.form.get('name', 'Bạn')
    uploaded_file = request.files.get('image')
    image_base64 = request.form.get('image_base64')  # Ảnh đã căn chỉnh trong trình duyệt

    # --- Nền thiệp ---
    base_card = Image.open(BASE_CARD_PATH).convert('RGBA')

    # --- Mở ảnh người dùng ---
    user_img = None
    if image_base64 and image_base64.startswith('data:image'):
        # Ảnh đã được crop/căn chỉnh và mã hóa base64
        header, data = image_base64.split(',', 1)
        user_img = Image.open(BytesIO(base64.b64decode(data))).convert('RGBA')
    elif uploaded_file and uploaded_file.filename != '':
        # Nếu người dùng upload ảnh gốc (không căn chỉnh)
        img_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(img_path)
        user_img = Image.open(img_path).convert('RGBA')

    # --- Dán ảnh lên thiệp ---
    if user_img is not None:
        # Ảnh base64 đã là hình tròn đúng vị trí khuôn mặt rồi
        user_img = user_img.resize((403, 415), Image.Resampling.LANCZOS)

        # Tạo mask tròn mượt để tránh viền cứng
        mask = create_circle_mask(user_img.size)
        user_img.putalpha(mask)

        # Vị trí trung tâm để dán ảnh
        circle_center = (base_card.width // 2, 561.5)
        paste_pos = (
            round(circle_center[0] - user_img.width / 2),
            round(circle_center[1] - user_img.height / 2)
        )

        # Dán ảnh lên nền
        layer = Image.new('RGBA', base_card.size, (0, 0, 0, 0))
        layer.paste(user_img, paste_pos, user_img)
        base_card = Image.alpha_composite(base_card, layer)

    # --- Viết tên người nhận ---
    draw = ImageDraw.Draw(base_card)
    try:
        font_name = ImageFont.truetype(FONT_PATH, 51)
    except:
        font_name = ImageFont.load_default()

    name_y = 810
    bbox_name = draw.textbbox((0, 0), name, font=font_name)
    text_w = bbox_name[2] - bbox_name[0]
    draw.text(
        ((base_card.width - text_w) / 2, name_y),
        name,
        font=font_name,
        fill=(204, 153, 0)  # màu vàng kim
    )

    # --- Lưu file kết quả ---
    output_filename = f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_path = os.path.join(CARD_FOLDER, output_filename)

    # Ghép với nền trắng để tránh bị đen khi hiển thị
    bg_white = Image.new("RGBA", base_card.size, (255, 255, 255, 255))
    result = Image.alpha_composite(bg_white, base_card)
    result.save(output_path)

    return render_template('result.html', card_filename=output_filename, name=name)


@app.route('/download/<filename>')
def download_card(filename):
    return send_from_directory(CARD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
