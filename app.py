from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import numpy as np
import os
import base64
import threading
import time
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/output', exist_ok=True)

# ─── Estado Global ───────────────────────────────────────────────
camera_state = {
    'active': False,
    'effect': None,
    'cap': None,
    'lock': threading.Lock()
}

video_state = {
    'active': False,
    'path': None,
    'cap': None,
    'tracker': None,
    'template': None,
    'bbox': None,
    'tracking': False,
    'lock': threading.Lock()
}

# ─── Utilitários ─────────────────────────────────────────────────
def apply_effect(frame, effect):
    if effect == 'gray':
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif effect == 'negative':
        return cv2.bitwise_not(frame)
    elif effect == 'binary':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return out
    elif effect == 'blur_mean':
        return cv2.blur(frame, (5, 5))
    elif effect == 'blur_median':
        return cv2.medianBlur(frame, 5)
    elif effect == 'canny':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, 100, 200)
    elif effect == 'erode':
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.erode(frame, kernel, iterations=1)
    elif effect == 'dilate':
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.dilate(frame, kernel, iterations=1)
    elif effect == 'open':
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    elif effect == 'close':
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
    return frame

def frame_to_jpg(frame):
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return buf.tobytes()

def criar_tracker():
    if hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerKCF_create()
    elif hasattr(cv2, "TrackerKCF_create"):
        return cv2.TrackerKCF_create()
    return None

# ─── Rotas Principais ────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
def camera_page():
    return render_template('camera.html')

@app.route('/image')
def image_page():
    return render_template('image.html')

@app.route('/tracking')
def tracking_page():
    return render_template('tracking.html')

# ─── API Câmera ──────────────────────────────────────────────────
def gen_camera_frames():
    with camera_state['lock']:
        if camera_state['cap'] is None or not camera_state['cap'].isOpened():
            camera_state['cap'] = cv2.VideoCapture(0)
        camera_state['active'] = True

    while camera_state['active']:
        with camera_state['lock']:
            if camera_state['cap'] is None:
                break
            ret, frame = camera_state['cap'].read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        effect = camera_state.get('effect')
        if effect:
            frame = apply_effect(frame, effect)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_to_jpg(frame) + b'\r\n')
        time.sleep(0.03)

@app.route('/api/camera/stream')
def camera_stream():
    return Response(gen_camera_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/effect', methods=['POST'])
def set_camera_effect():
    data = request.get_json()
    camera_state['effect'] = data.get('effect')
    return jsonify({'status': 'ok', 'effect': camera_state['effect']})

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    camera_state['active'] = False
    with camera_state['lock']:
        if camera_state['cap']:
            camera_state['cap'].release()
            camera_state['cap'] = None
    return jsonify({'status': 'stopped'})

# ─── API Imagem ──────────────────────────────────────────────────
@app.route('/api/image/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    effect = request.form.get('effect', 'none')

    np_arr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Imagem inválida'}), 400

    processed = apply_effect(img, effect) if effect != 'none' else img

    if len(processed.shape) == 2:
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)

    _, buf = cv2.imencode('.png', processed)
    b64 = base64.b64encode(buf).decode()
    return jsonify({'image': f'data:image/png;base64,{b64}'})

@app.route('/api/image/bitplanes', methods=['POST'])
def bit_planes():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo'}), 400

    file = request.files['file']
    np_arr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Imagem inválida'}), 400

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    planes = []
    for i in range(8):
        plane = np.bitwise_and(gray, 2 ** i)
        plane[plane > 0] = 255
        _, buf = cv2.imencode('.png', plane)
        b64 = base64.b64encode(buf).decode()
        planes.append({'bit': i, 'image': f'data:image/png;base64,{b64}'})

    return jsonify({'planes': planes})

# ─── API Rastreamento ─────────────────────────────────────────────
@app.route('/api/tracking/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo'}), 400
    file = request.files['file']
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'track_video.mp4')
    file.save(path)
    video_state['path'] = path
    video_state['tracking'] = False
    video_state['tracker'] = None
    video_state['template'] = None
    return jsonify({'status': 'uploaded', 'path': path})

@app.route('/api/tracking/select_roi', methods=['POST'])
def select_roi():
    data = request.get_json()
    x = int(data['x'])
    y = int(data['y'])
    w = int(data['w'])
    h = int(data['h'])

    if not video_state.get('path'):
        return jsonify({'error': 'Nenhum vídeo carregado'}), 400

    cap = cv2.VideoCapture(video_state['path'])
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return jsonify({'error': 'Erro ao ler frame'}), 400

    fh, fw = frame.shape[:2]
    x = int(x * fw)
    y = int(y * fh)
    w = int(w * fw)
    h = int(h * fh)

    bbox = (x, y, w, h)
    template = frame[y:y+h, x:x+w]
    tracker = criar_tracker()
    if tracker:
        tracker.init(frame, bbox)

    video_state['bbox'] = bbox
    video_state['template'] = template
    video_state['tracker'] = tracker
    video_state['tracking'] = True
    video_state['frame_pos'] = 0

    return jsonify({'status': 'roi_set'})

def gen_tracking_frames():
    if not video_state.get('path'):
        return

    cap = cv2.VideoCapture(video_state['path'])

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break

        tracker = video_state.get('tracker')
        template = video_state.get('template')

        if tracker and video_state.get('tracking'):
            success, box = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 100, 255), 2)
                cv2.putText(frame, "TRACKING", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)
            else:
                if template is not None:
                    res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(res)
                    if max_val > 0.7:
                        x, y = max_loc
                        w, h = template.shape[1], template.shape[0]
                        new_bbox = (x, y, w, h)
                        new_tracker = criar_tracker()
                        if new_tracker:
                            new_tracker.init(frame, new_bbox)
                            video_state['tracker'] = new_tracker
                            video_state['bbox'] = new_bbox
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 150), 2)
                        cv2.putText(frame, "RECOVERED", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 150), 2)
                    else:
                        cv2.putText(frame, "SEARCHING...", (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 80, 80), 2)
        else:
            cv2.putText(frame, "Selecione ROI para rastrear", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_to_jpg(frame) + b'\r\n')
        time.sleep(0.033)

    cap.release()

@app.route('/api/tracking/stream')
def tracking_stream():
    return Response(gen_tracking_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/tracking/reset', methods=['POST'])
def reset_tracking():
    video_state['tracking'] = False
    video_state['tracker'] = None
    video_state['template'] = None
    video_state['bbox'] = None
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
