from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io, os

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

        # --- Nếu có ảnh khách ---
        if uploaded_file and uploaded_file.filename != '':
            user_img = Image.open(uploaded_file.stream).convert('RGBA')

            # 🔹 1. Crop ảnh thành hình vuông để không bị méo
            w, h = user_img.size
            min_side = min(w, h)
            user_img = user_img.crop((
                (w - min_side) // 2,
                (h - min_side) // 2,
                (w + min_side) // 2,
                (h + min_side) // 2
            ))

            # 🔹 2. Resize cho hợp bố cục (ảnh nằm bên trái)
            frame_size = 320  # bạn có thể tinh chỉnh (300–350 tuỳ bố cục)
            user_img = user_img.resize((frame_size, frame_size))

            # 🔹 3. Bo tròn ảnh cho đẹp (tuỳ chọn)
            mask = Image.new("L", (frame_size, frame_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, frame_size, frame_size), fill=255)
            user_img.putalpha(mask)

            # 🔹 4. Dán ảnh vào bên trái (chỉnh toạ độ cho khớp)
            pos_x, pos_y = 120, (bg.height - frame_size) // 2 - 60
            bg.alpha_composite(user_img, (pos_x, pos_y))

            # 🔹 5. Ghi tên người ngay dưới ảnh
            font_path = "arial.ttf"
            font = ImageFont.truetype(font_path, 50)

            bbox = draw.textbbox((0, 0), name, font=font)
            text_w = bbox[2] - bbox[0]
            text_x = pos_x + (frame_size - text_w) / 2
            text_y = pos_y + frame_size + 30  # cách ảnh 30px

            draw.text((text_x, text_y), name, fill=(245, 205, 150), font=font)

        # --- Xuất kết quả ---
        buf = io.BytesIO()
        bg.convert('RGB').save(buf, format='PNG')
        buf.seek(0)

        return send_file(
            buf,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'thiep_{name}.png'
        )

    return render_template('index.html')


#if __name__ == '__main__':
#    app.run(debug=True)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
