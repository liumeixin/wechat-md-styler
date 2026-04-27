#!/usr/bin/env python3
"""
微信公众号 Markdown 排版工具 - Flask Web 应用
=============================================
交互式网页，支持：
- Markdown 输入
- 模板选择 + 实时预览
- 一键复制到剪贴板

用法: python app.py
访问: http://localhost:8080
"""

import os
import base64
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from pathlib import Path

app = Flask(__name__)

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


def get_css(template_name: str) -> str:
    """获取指定模板的 CSS"""
    css_path = TEMPLATES_DIR / f"{template_name}.css"
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# HTML 模板（嵌入式）
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号 Markdown 排版工具</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .header p {
            opacity: 0.9;
            margin-top: 5px;
            font-size: 14px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            display: flex;
            gap: 20px;
        }
        
        .panel {
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
        }
        
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .template-selector {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .template-btn {
            padding: 6px 14px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        
        .template-btn:hover {
            border-color: #667eea;
        }
        
        .template-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: transparent;
            color: white;
        }
        
        .editor {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .editor textarea {
            flex: 1;
            width: 100%;
            min-height: 400px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: none;
        }
        
        .editor textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .preview {
            flex: 1;
            min-height: 400px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: auto;
            background: white;
        }
        
        .preview-content {
            padding: 20px;
        }
        
        .toolbar {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-success:hover {
            background: #059669;
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 6px;
            font-size: 13px;
            display: none;
        }
        
        .status.success {
            display: block;
            background: #d1fae5;
            color: #065f46;
        }
        
        .status.error {
            display: block;
            background: #fee2e2;
            color: #991b1b;
        }
        
        .tips {
            margin-top: 15px;
            padding: 12px;
            background: #fef3c7;
            border-radius: 6px;
            font-size: 13px;
            color: #92400e;
        }
        
        .tips strong {
            display: block;
            margin-bottom: 5px;
        }
        
        /* 加载动画 */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 900px) {
            .container {
                flex-direction: column;
            }
            
            .panel {
                min-height: auto;
            }
            
            .editor textarea {
                min-height: 250px;
            }
            
            .preview {
                min-height: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📝 微信公众号 Markdown 排版工具</h1>
        <p>输入 Markdown → 选择模板 → 一键复制到微信</p>
    </div>
    
    <div class="container">
        <!-- 输入面板 -->
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">📄 Markdown 输入</span>
                <button class="btn btn-secondary" onclick="loadExample()">加载示例</button>
            </div>
            <div class="editor">
                <textarea id="markdown-input" placeholder="在这里输入 Markdown 内容..."></textarea>
            </div>
            <div class="toolbar">
                <button class="btn btn-primary" onclick="convert()">
                    <span>🔄 转换</span>
                </button>
                <button class="btn btn-secondary" onclick="clearInput()">
                    <span>🗑️ 清空</span>
                </button>
            </div>
            <div id="status" class="status"></div>
        </div>
        
        <!-- 预览面板 -->
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">👁️ 预览</span>
                <div class="template-selector" id="template-buttons">
                    <!-- 模板按钮将由 JS 生成 -->
                </div>
            </div>
            <div class="preview" id="preview-container">
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 10px;">转换中...</p>
                </div>
                <div class="preview-content" id="preview-content">
                    <p style="color: #999; text-align: center; padding: 40px;">
                        输入 Markdown 并点击"转换"按钮预览效果
                    </p>
                </div>
            </div>
            <div class="toolbar">
                <button class="btn btn-success" onclick="copyToClipboard()" id="copy-btn" disabled>
                    <span>📋 一键复制</span>
                </button>
            </div>
            <div class="tips">
                <strong>💡 使用提示：</strong>
                1. 点击"一键复制"后，完整的 HTML 已复制到剪贴板<br>
                2. 打开微信公众号后台，Ctrl+V 粘贴即可<br>
                3. 如样式丢失，可能是微信不兼容该 CSS
            </div>
        </div>
    </div>

    <script>
        let currentTemplate = 'elegant';
        let currentHtml = '';
        const templates = {{ templates | tojson }};
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initTemplateButtons();
        });
        
        // 初始化模板按钮
        function initTemplateButtons() {
            const container = document.getElementById('template-buttons');
            container.innerHTML = templates.map(t => 
                `<button class="template-btn ${t === currentTemplate ? 'active' : ''}" 
                        onclick="selectTemplate('${t}')">${getTemplateName(t)}</button>`
            ).join('');
        }
        
        // 获取模板显示名称
        function getTemplateName(name) {
            const names = {
                'elegant': '优雅紫',
                'tech': '科技蓝',
                'minimal': '简约白',
                'warm': '暖色调',
                'dark': '暗夜'
            };
            return names[name] || name;
        }
        
        // 选择模板
        function selectTemplate(template) {
            currentTemplate = template;
            initTemplateButtons();
            // 如果已有内容，自动重新转换
            const input = document.getElementById('markdown-input').value;
            if (input.trim()) {
                convert();
            }
        }
        
        // 转换
        async function convert() {
            const input = document.getElementById('markdown-input').value;
            if (!input.trim()) {
                showStatus('请输入 Markdown 内容', 'error');
                return;
            }
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('preview-content').style.display = 'none';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        markdown: input,
                        template: currentTemplate
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentHtml = data.html;
                    document.getElementById('preview-content').innerHTML = data.html;
                    document.getElementById('copy-btn').disabled = false;
                    showStatus('✅ 转换成功！', 'success');
                } else {
                    showStatus('转换失败: ' + data.error, 'error');
                }
            } catch (e) {
                showStatus('请求失败: ' + e.message, 'error');
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('preview-content').style.display = 'block';
            }
        }
        
        // 一键复制
        async function copyToClipboard() {
            if (!currentHtml) return;
            
            try {
                // 复制完整 HTML 到剪贴板
                await navigator.clipboard.writeText(currentHtml);
                showStatus('✅ 已复制到剪贴板！去微信公众号粘贴吧', 'success');
            } catch (e) {
                // 如果 API 失败，尝试用旧方法
                try {
                    const textarea = document.createElement('textarea');
                    textarea.value = currentHtml;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    showStatus('✅ 已复制到剪贴板！去微信公众号粘贴吧', 'success');
                } catch (e2) {
                    showStatus('复制失败，请手动复制预览内容', 'error');
                }
            }
        }
        
        // 加载示例
        function loadExample() {
            const example = `# 微信公众号排版测试

这是一段**正文内容**，用来测试排版效果。

## 二级标题

### 三级标题

正文段落，继续测试。微信公众号对 CSS 支持有限，需要注意：

- 列表项 1
- 列表项 2
- 列表项 3

> 这是引用块，可以用来强调重要内容

### 代码测试

行内代码：`console.log('hello')`

代码块：

\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`

### 链接和强调

这是[链接文字](https://example.com)。

**粗体文字**和*斜体文字*。

---

分割线测试

| 表格 | 表头 | 测试 |
|------|------|------|
| 单元格1 | 单元格2 | 单元格3 |
| 单元格4 | 单元格5 | 单元格6 |

---

> 转换后点击"一键复制"，然后去微信公众号后台粘贴即可！
`;
            document.getElementById('markdown-input').value = example;
            convert();
        }
        
        // 清空输入
        function clearInput() {
            document.getElementById('markdown-input').value = '';
            document.getElementById('preview-content').innerHTML = '<p style="color: #999; text-align: center; padding: 40px;">输入 Markdown 并点击"转换"按钮预览效果</p>';
            document.getElementById('copy-btn').disabled = true;
            currentHtml = '';
            hideStatus();
        }
        
        // 显示状态
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }
        
        // 隐藏状态
        function hideStatus() {
            document.getElementById('status').className = 'status';
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE, templates=get_templates())


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
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     微信公众号 Markdown 排版工具                            ║
║     访问地址: http://localhost:{port}                       ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()