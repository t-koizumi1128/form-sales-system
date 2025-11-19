"""
メールフォーム営業システム - Railway版
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import threading
import time
import io
import csv
import os

app = Flask(__name__)
CORS(app)

# データベースパス
DB_PATH = 'sales_system.db'

# データベース初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 基本設定テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company_name TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # クロール結果テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS crawl_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            company_name TEXT,
            url TEXT UNIQUE,
            form_url TEXT,
            has_captcha INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            submitted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 実行履歴テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS execution_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            total_found INTEGER,
            total_submitted INTEGER,
            success_count INTEGER,
            fail_count INTEGER,
            captcha_count INTEGER,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'running'
        )
    ''')
    
    conn.commit()
    conn.close()

# API エンドポイント

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """設定一覧取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM settings ORDER BY created_at DESC')
    settings = []
    for row in c.fetchall():
        settings.append({
            'id': row[0],
            'name': row[1],
            'company_name': row[2],
            'contact_person': row[3],
            'email': row[4],
            'phone': row[5],
            'message': row[6],
            'created_at': row[7]
        })
    conn.close()
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def create_setting():
    """設定作成"""
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO settings (name, company_name, contact_person, email, phone, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('company_name'),
        data.get('contact_person'),
        data.get('email'),
        data.get('phone'),
        data.get('message')
    ))
    conn.commit()
    setting_id = c.lastrowid
    conn.close()
    return jsonify({'id': setting_id, 'message': '設定を保存しました'})

@app.route('/api/settings/<int:setting_id>', methods=['PUT'])
def update_setting(setting_id):
    """設定更新"""
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE settings 
        SET name=?, company_name=?, contact_person=?, email=?, phone=?, message=?
        WHERE id=?
    ''', (
        data.get('name'),
        data.get('company_name'),
        data.get('contact_person'),
        data.get('email'),
        data.get('phone'),
        data.get('message'),
        setting_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': '設定を更新しました'})

@app.route('/api/settings/<int:setting_id>', methods=['DELETE'])
def delete_setting(setting_id):
    """設定削除"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM settings WHERE id=?', (setting_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '設定を削除しました'})

@app.route('/api/crawl/demo', methods=['POST'])
def demo_crawl():
    """デモクロール - サンプルデータを生成"""
    data = request.json
    keyword = data.get('keyword', 'サンプル企業')
    
    # デモ用のサンプルデータ
    demo_companies = [
        {'company_name': f'{keyword} 株式会社 A', 'url': f'https://example-a.com', 'form_url': f'https://example-a.com/contact', 'has_captcha': 0},
        {'company_name': f'{keyword} 株式会社 B', 'url': f'https://example-b.com', 'form_url': f'https://example-b.com/inquiry', 'has_captcha': 1},
        {'company_name': f'{keyword} 有限会社 C', 'url': f'https://example-c.com', 'form_url': f'https://example-c.com/contact', 'has_captcha': 0},
        {'company_name': f'{keyword} 合同会社 D', 'url': f'https://example-d.com', 'form_url': f'https://example-d.com/form', 'has_captcha': 0},
        {'company_name': f'{keyword} 株式会社 E', 'url': f'https://example-e.com', 'form_url': f'https://example-e.com/contact', 'has_captcha': 1},
    ]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    inserted = 0
    for company in demo_companies:
        try:
            unique_url = f"{company['url']}?t={int(time.time())}"
            c.execute('''
                INSERT INTO crawl_results 
                (keyword, company_name, url, form_url, has_captcha)
                VALUES (?, ?, ?, ?, ?)
            ''', (keyword, company['company_name'], unique_url, company['form_url'], company['has_captcha']))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': f'{inserted}件のデモデータを追加しました', 'count': inserted})

@app.route('/api/submit/demo', methods=['POST'])
def demo_submit():
    """デモ送信"""
    data = request.json
    target_count = data.get('target_count', 3)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, url, has_captcha FROM crawl_results WHERE status="pending" LIMIT ?', (target_count,))
    pending = c.fetchall()
    
    success = 0
    failed = 0
    skipped = 0
    
    for row in pending:
        form_id, url, has_captcha = row
        
        if has_captcha:
            c.execute('UPDATE crawl_results SET status="skipped", error_message="CAPTCHAが検出されました", submitted_at=? WHERE id=?', (datetime.now(), form_id))
            skipped += 1
        else:
            import random
            if random.random() > 0.2:
                c.execute('UPDATE crawl_results SET status="success", submitted_at=? WHERE id=?', (datetime.now(), form_id))
                success += 1
            else:
                c.execute('UPDATE crawl_results SET status="failed", error_message="タイムアウト（デモ）", submitted_at=? WHERE id=?', (datetime.now(), form_id))
                failed += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '送信完了（デモモード）', 'success': success, 'failed': failed, 'skipped': skipped})

@app.route('/api/results', methods=['GET'])
def get_results():
    """結果一覧取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    status_filter = request.args.get('status')
    if status_filter:
        c.execute('SELECT * FROM crawl_results WHERE status=? ORDER BY created_at DESC', (status_filter,))
    else:
        c.execute('SELECT * FROM crawl_results ORDER BY created_at DESC')
    
    results = []
    for row in c.fetchall():
        results.append({
            'id': row[0], 'keyword': row[1], 'company_name': row[2], 'url': row[3],
            'form_url': row[4], 'has_captcha': row[5], 'status': row[6],
            'error_message': row[7], 'submitted_at': row[8], 'created_at': row[9]
        })
    conn.close()
    return jsonify(results)

@app.route('/api/results/export', methods=['GET'])
def export_results():
    """CSVエクスポート"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM crawl_results ORDER BY created_at DESC')
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'キーワード', '企業名', 'URL', 'フォームURL', 'CAPTCHA有無', 'ステータス', 'エラー', '送信日時', '作成日時'])
    
    for row in c.fetchall():
        writer.writerow(row)
    
    conn.close()
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """統計情報取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM crawl_results')
    total = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM crawl_results WHERE status="success"')
    success = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM crawl_results WHERE status="failed"')
    failed = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM crawl_results WHERE has_captcha=1 OR status="skipped"')
    captcha = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM crawl_results WHERE status="pending"')
    pending = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total': total, 'success': success, 'failed': failed,
        'captcha': captcha, 'pending': pending,
        'success_rate': round(success / total * 100, 1) if total > 0 else 0
    })

@app.route('/api/results/clear', methods=['POST'])
def clear_results():
    """結果をクリア"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM crawl_results')
    conn.commit()
    conn.close()
    return jsonify({'message': 'すべての結果をクリアしました'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
