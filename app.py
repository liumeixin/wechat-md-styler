#!/usr/bin/env python3
"""
微信公众号 Markdown 排版工具 - Flask Web 应用
=============================================
使用外部模板文件，避免 Jinja2 tojson 过滤器解析问题

用法: python app.py
访问: http://localhost:8080
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pathlib import Path
from datetime import datetime

# 设置时区
os.environ['TZ'] = 'Asia/Shanghai'

app = Flask(__name__, template_folder='templates_flask')

# 解除图片加载限制
@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = "img-src * data: blob:;"
    return response

# 记录容器启动时间
CONTAINER_START_TIME = datetime.now().strftime('%Y年%m月%d日%H时%M分')

# 配置
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
CONFIG_FILE = BASE_DIR / "config.yaml"

# 获取可用模板
def get_templates():
    """获取所有可用的 CSS 模板"""
    templates = []
    if TEMPLATES_DIR.exists():
        for f in TEMPLATES_DIR.glob("*.css"):
            templates.append(f.stem)
    return templates if templates else ["elegant"]


@app.route('/')
def index():
    """主页"""
    return render_template('index.html', templates=get_templates(), start_time=CONTAINER_START_TIME)


@app.route('/convert', methods=['POST'])
def convert():
    """转换 Markdown 为 HTML"""
    try:
        data = request.get_json()
        markdown = data.get('markdown', '')
        template = data.get('template', 'elegant')
        
        if not markdown:
            return jsonify({'success': False, 'error': '输入为空'})
        
        # 导入转换器
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from wechat_styler import WeChatStyler
        
        # 转换
        styler = WeChatStyler(template=template)
        html = styler.convert(markdown)
        
        return jsonify({'success': True, 'html': html})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/templates/<path:filename>')
def serve_css(filename):
    """提供 CSS 文件"""
    return send_from_directory(TEMPLATES_DIR, filename)


def main():
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("""
╔════════════════════════════════════════════════════════════╗
║     微信公众号 Markdown 排版工具                            ║
║     访问地址: http://localhost:{port}                       ║
╚════════════════════════════════════════════════════════════╝
    """.format(port=port))
    
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()