from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os
from datetime import datetime

app = Flask(__name__)

# --- Đường dẫn tuyệt đối ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
CARD_FOLDER = os.path.join('static', 'cards')
FONT_PATH = os.path.join('static', 'fonts', 'PLAYFAIRDISPLAY-REGULAR.TTF')
BASE_CARD_PATH = os.path.join('static', 'invite_bg.png')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

def crop_center_square(img):
    w, h = img.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    return img.crop((left, top, right, bottom))

@app.route('/create_card', methods=['POST'])
def create_card():
    name = request.form.get('name', 'Bạn')
    uploaded_file = request.files.get('image')

    base_card = Image.open(BASE_CARD_PATH).convert('RGBA')

    # --- Thêm ảnh người ---
    if uploaded_file and uploaded_file.filename != '':
        img_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(img_path)

        user_img = Image.open(img_path).convert('RGBA')
        user_img = crop_center_square(user_img) 
        user_img = user_img.resize((403, 415), Image.Resampling.LANCZOS)

        # Bo tròn ảnh
        mask = Image.new('L', user_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, user_img.size[0], user_img.size[1]), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(1.5))
        user_img.putalpha(mask)

        # Căn giữa vùng tròn
        circle_center = (base_card.width // 2, 560)  # chỉnh lại y nếu chưa khớp
        paste_pos = (
            circle_center[0] - user_img.width // 2,
            circle_center[1] - user_img.height // 2
        )
        base_card.paste(user_img, paste_pos, user_img)

    # --- Viết chữ ---
    draw = ImageDraw.Draw(base_card)
    try:
        font_name = ImageFont.truetype(FONT_PATH, 51)  # chữ tên
        font_text = ImageFont.truetype(FONT_PATH, 38)  # chữ chúc mừng
    except:
        font_name = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Tên người nằm trên gạch vàng
    name_y = 810  # chỉnh lại cho đúng với template của bạn
    bbox_name = draw.textbbox((0, 0), name, font=font_name)
    text_w = bbox_name[2] - bbox_name[0]
    draw.text(
        ((base_card.width - text_w) / 2, name_y),
        name,
        font=font_name,
        fill=(204, 153, 0)  # màu vàng đẹp, có thể đổi thành (255, 215, 0)
    )

    # --- Lưu thiệp ---
    output_filename = f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_path = os.path.join(CARD_FOLDER, output_filename)
    base_card.save(output_path)

    return render_template('result.html', card_filename=output_filename, name=name)


@app.route('/download/<filename>')
def download_card(filename):
    return send_from_directory(CARD_FOLDER, filename, as_attachment=True)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)