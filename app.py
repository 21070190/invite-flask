from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
import io, os, base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name'].strip()
        uploaded_file = request.files.get('photo')

        if not name:
            return render_template('index.html', error="Vui lòng nhập tên!")

        # --- Nạp ảnh nền mẫu ---
        bg_path = os.path.join(os.path.dirname(__file__), 'static', 'invite_bg.jpg')
        bg = Image.open(bg_path).convert('RGBA')
        draw = ImageDraw.Draw(bg)

        # --- Nếu có ảnh người dùng ---
        if uploaded_file and uploaded_file.filename != '':
            uploaded_file.stream.seek(0)
            user_img = Image.open(uploaded_file.stream).convert('RGBA')

            # 🔹 1. Crop ảnh thành hình vuông
            w, h = user_img.size
            min_side = min(w, h)
            user_img = user_img.crop((
                (w - min_side) // 2,
                (h - min_side) // 2,
                (w + min_side) // 2,
                (h + min_side) // 2
            ))

            # 🔹 2. Resize ảnh cho hợp bố cục
            frame_size = 320
            user_img = user_img.resize((frame_size, frame_size))

            # 🔹 3. Bo tròn ảnh (mask)
            mask = Image.new("L", (frame_size, frame_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, frame_size, frame_size), fill=255)
            user_img.putalpha(mask)

            # 🔹 4. Dán ảnh vào thiệp
            pos_x, pos_y = 120, (bg.height - frame_size) // 2 - 60
            bg.alpha_composite(user_img, (pos_x, pos_y))

            # 🔹 5. Ghi tên người dưới ảnh
            font_path = os.path.join(app.root_path, 'static', 'fonts', 'Roboto_Condensed-Regular.ttf')
            font = ImageFont.truetype(font_path, 50)
            bbox = draw.textbbox((0, 0), name, font=font)
            text_w = bbox[2] - bbox[0]
            text_x = pos_x + (frame_size - text_w) / 2
            text_y = pos_y + frame_size + 30
            draw.text((text_x, text_y), name, fill=(245, 205, 150), font=font)

        # --- Chuyển ảnh sang base64 để hiển thị ---
        buf = io.BytesIO()
        bg.convert('RGB').save(buf, format='PNG')
        data = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Hiển thị trang kết quả
        return render_template('result.html', name=name, img_data=data)

    return render_template('index.html')


#if __name__ == '__main__':
#    app.run(debug=True)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
