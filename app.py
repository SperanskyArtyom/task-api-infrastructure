from flask import Flask, jsonify, request
import signal
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Простая in-memory база данных
tasks = [
    {"id": 1, "title": "Изучить Docker", "completed": False},
    {"id": 2, "title": "Написать API", "completed": True}
]

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Получить все задачи"""
    logger.info("GET /api/tasks")
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Получить задачу по ID"""
    logger.info(f"GET /api/tasks/{task_id}")
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создать новую задачу"""
    logger.info("POST /api/tasks")
    if not request.json or 'title' not in request.json:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = {
        "id": len(tasks) + 1,
        "title": request.json['title'],
        "completed": request.json.get('completed', False)
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Удалить задачу"""
    logger.info(f"DELETE /api/tasks/{task_id}")
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({"result": "Task deleted"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task-api"})

@app.route('/')
def index():
    return jsonify({
        "name": "Task API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "tasks": "/api/tasks"
        }
    })

def graceful_shutdown(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# Регистрация обработчиков сигналов
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == '__main__':
    logger.info("Starting Task API server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
