from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
from ultralytics import YOLO
import os
import uuid
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Загружаем модель YOLOv8
model = YOLO('yolov8n.pt')

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            pizza_count INTEGER,
            total_objects INTEGER,
            processing_time REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Файл не загружен'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        os.makedirs('static/uploads', exist_ok=True)
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = f'static/uploads/{filename}'
        file.save(filepath)
        
        with open(filepath, 'rb') as f:
            image_bytes = f.read()
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        import time
        start_time = time.time()
        results = model(img)
        processing_time = time.time() - start_time
        
        # ПОДСЧЁТ ПИЦЦ - ПОИСК ПО ИМЕНИ КЛАССА
        pizza_count = 0
        total_objects = 0
        pizza_confidence = []
        
        if results[0].boxes is not None:
            total_objects = len(results[0].boxes)
            
            print(" Все объекты на фото:")
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                # Получаем имя класса из модели
                class_name = model.names[class_id]
                print(f"   Класс: {class_id} ({class_name}), уверенность: {confidence:.2f}")
                
                # Ищем по имени класса (регистр не важен)
                if 'pizza' in class_name.lower() and confidence > 0.3:
                    pizza_count += 1
                    pizza_confidence.append(confidence)
        
        print(f" Всего объектов: {total_objects}")
        print(f" Пицц найдено: {pizza_count}")
        if pizza_confidence:
            print(f" Уверенность: {min(pizza_confidence):.2f} - {max(pizza_confidence):.2f}")
        
        # Визуализация
        output_img = results[0].plot()
        cv2.putText(output_img, f'Pizzas: {pizza_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        os.makedirs('static/results', exist_ok=True)
        result_filename = f"result_{filename}"
        result_path = f'static/results/{result_filename}'
        cv2.imwrite(result_path, output_img)
        
        # Сохраняем в историю
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (timestamp, filename, pizza_count, total_objects, processing_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), filename, pizza_count, total_objects, round(processing_time, 3)))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'pizza_count': pizza_count,
            'result_image': result_path,
            'processing_time': round(processing_time, 3),
            'total_objects': total_objects,
            'debug': f"Найдено объектов: {total_objects}, из них пицц: {pizza_count}"
        })
    
    except Exception as e:
        print(f" Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)