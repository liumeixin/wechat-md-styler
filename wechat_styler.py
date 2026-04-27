#!/usr/bin/env python3
"""
微信公众号 Markdown 排版工具
===========================
将 Markdown 文件转换为微信公众号可用的 HTML 格式

用法:
    python wechat_styler.py input.md -t elegant -o output.html
    python wechat_styler.py input.md --preview  # 预览模式
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


class WeChatStyler:
    """微信公众号 Markdown 排版转换器"""
    
    def __init__(self, template: str = "elegant", config_path: Optional[str] = None):
        self.template = template
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.css = self._load_css(template)
        
    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """加载配置"""
        if config_path is None:
            config_path = self.base_dir / "config.yaml"
        
        if yaml is None:
            return {"default_template": "elegant", "available_templates": ["elegant"]}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {"default_template": "elegant", "available_templates": ["elegant"]}
    
    def _load_css(self, template: str) -> str:
        """加载 CSS 模板"""
        css_path = self.base_dir / "templates" / f"{template}.css"
        
        # 如果指定模板不存在，回退到默认
        if not css_path.exists():
            default = self.config.get("default_template", "elegant")
            css_path = self.base_dir / "templates" / f"{default}.css"
        
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return self._get_default_css()
    
    def _get_default_css(self) -> str:
        """内置默认 CSS（优雅紫主题）"""
        return """body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:17px;line-height:1.8;color:rgb(89,89,89)}h1,h2,h3,h4,h5,h6{color:rgb(0,0,0);font-weight:bold;margin:1em 0 .5em 0;line-height:1.5}h1{font-size:22px;text-align:center}h2{font-size:20px}h3{font-size:18px}p{margin:0;padding:8px 0}a{color:rgb(145,109,213);text-decoration:none;border-bottom:1px solid rgb(145,109,213)}strong,b{color:rgb(145,109,213);font-weight:bold}code{font-family:Consolas,Monaco,Menlo,monospace;font-size:14px;background-color:rgba(27,31,35,.05);color:rgb(145,109,213);padding:2px 4px;border-radius:4px}pre{background-color:rgba(27,31,35,.05);padding:12px 16px;border-radius:4px;overflow-x:auto;margin:12px 0}pre code{background:none;color:#333}blockquote{margin:12px 0;padding:12px 16px;border-left:4px solid rgb(145,109,213);background-color:rgb(246,238,255)}ul,ol{margin:12px 0;padding-left:24px}li{margin:6px 0}img{max-width:100%;height:auto;display:block;margin:16px auto;border-radius:4px}table{width:100%;border-collapse:collapse;margin:16px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background-color:rgb(246,238,255)}"""
    
    def convert(self, markdown: str) -> str:
        """将 Markdown 转换为 HTML"""
        html = self._markdown_to_html(markdown)
        return self._wrap_html(html)
    
    def _markdown_to_html(self, md: str) -> str:
        """Markdown 转 HTML 的核心逻辑"""
        html = md
        
        # 1. 代码块 ```...```
        html = re.sub(
            r'```(\w*)\n(.*?)```',
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # 2. 行内代码 `...`
        html = re.sub(
            r'`([^`]+)`',
            r'<code>\1</code>',
            html
        )
        
        # 3. 标题处理
        lines = html.split('\n')
        new_lines = []
        
        for line in lines:
            # H1: # 标题
            if line.startswith('# '):
                new_lines.append(f'<h1>{line[2:]}</h1>')
            # H2: ## 标题
            elif line.startswith('## '):
                new_lines.append(f'<h2>{line[3:]}</h2>')
            # H3: ### 标题
            elif line.startswith('### '):
                new_lines.append(f'<h3>{line[4:]}</h3>')
            # H4: #### 标题
            elif line.startswith('#### '):
                new_lines.append(f'<h4>{line[5:]}</h4>')
            # 分割线
            elif re.match(r'^---+$', line) or re.match(r'^\*\*\*+$', line):
                new_lines.append('<hr>')
            # 普通段落
            else:
                new_lines.append(line)
        
        html = '\n'.join(new_lines)
        
        # 4. 强调 **粗体** 或 __粗体__
        html = re.sub(
            r'\*\*([^*]+)\*\*',
            r'<strong>\1</strong>',
            html
        )
        html = re.sub(
            r'__([^_]+)__',
            r'<strong>\1</strong>',
            html
        )
        
        # 5. 斜体 *斜体* 或 _斜体_
        html = re.sub(
            r'\*([^*]+)\*',
            r'<em>\1</em>',
            html
        )
        
        # 6. 图片 ![alt](url) （必须在链接之前处理）
        html = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'<img src="\2" alt="\1">',
            html
        )

        # 7. 链接 [文字](url)
        html = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            html
        )
        
        # 8. 无序列表
        html = re.sub(
            r'^- (.+)$',
            r'<li>\1</li>',
            html,
            flags=re.MULTILINE
        )
        
        # 9. 有序列表
        html = re.sub(
            r'^\d+\. (.+)$',
            r'<li>\1</li>',
            html,
            flags=re.MULTILINE
        )
        
        # 10. 引用块 > 文字
        html = re.sub(
            r'^> (.+)$',
            r'<blockquote>\1</blockquote>',
            html,
            flags=re.MULTILINE
        )
        
# 10. 段落处理：将连续的文本块包裹为 p
        # 注意：单行换行（无空行分隔）属于同一段落，双重换行（空行）才是段落分隔
        paragraphs = []
        in_list = False
        in_pre = False
        current_paragraph_lines = []  # 累积当前段落的行

        def flush_paragraph():
            """将累积的行合并为一个段落"""
            nonlocal current_paragraph_lines
            if current_paragraph_lines:
                # 合并多行，保留软换行（单\n转<br>）
                para_content = '<br>\n'.join(current_paragraph_lines)
                paragraphs.append(f'<p>{para_content}</p>')
                current_paragraph_lines = []

        for line in html.split('\n'):
            line_stripped = line.strip()
            
            # 跳过空行（段落分隔符）
            if not line_stripped:
                if in_list:
                    paragraphs.append('</ul>')
                    in_list = False
                else:
                    flush_paragraph()
                continue
            
            # 代码块和预格式化内容直接添加
            if line.startswith('<pre') or line.startswith('<code'):
                in_pre = True
                flush_paragraph()
                paragraphs.append(line)
            elif in_pre:
                paragraphs.append(line)
                if '</pre>' in line or '</code>' in line:
                    in_pre = False
            # 列表项
            elif line_stripped.startswith('<li>'):
                if not in_list:
                    flush_paragraph()
                    paragraphs.append('<ul>')
                    in_list = True
                paragraphs.append(line_stripped)
            # 标题
            elif line_stripped.startswith('<h'):
                flush_paragraph()
                paragraphs.append(line_stripped)
            # 引用块
            elif line_stripped.startswith('<blockquote'):
                flush_paragraph()
                paragraphs.append(line_stripped)
            # 分割线
            elif line_stripped == '<hr>':
                flush_paragraph()
                paragraphs.append(line_stripped)
            # 其他作为段落（累积多行）
            else:
                # 如果是图片标签，先 flush 段落再添加
                if line_stripped.startswith('<img'):
                    flush_paragraph()
                    paragraphs.append(line_stripped)
                else:
                    if in_list:
                        paragraphs.append('</ul>')
                        in_list = False
                    current_paragraph_lines.append(line_stripped)

        if in_list:
            paragraphs.append('</ul>')
        flush_paragraph()

        return '\n'.join(paragraphs)
    
    def _wrap_html(self, content: str) -> str:
        """包装成完整的 HTML 文档"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章</title>
    <style>
{self.css}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """转换文件"""
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown = f.read()
        
        html = self.convert(markdown)
        
        if output_path:
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ 已保存到: {output_path}")
        else:
            # 默认输出到同目录的 .html 文件
            output_file = input_file.with_suffix('.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ 已保存到: {output_file}")
        
        return html
    
    def list_templates(self) -> list:
        """列出可用模板"""
        templates_dir = self.base_dir / "templates"
        if templates_dir.exists():
            return [f.stem for f in templates_dir.glob("*.css")]
        return ["elegant"]


def main():
    parser = argparse.ArgumentParser(
        description="微信公众号 Markdown 排版工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python wechat_styler.py article.md              # 使用默认模板转换
  python wechat_styler.py article.md -t tech      # 使用科技蓝模板
  python wechat_styler.py article.md -l           # 列出所有模板
  python wechat_styler.py article.md --preview    # 预览模式
        """
    )
    
    parser.add_argument('input', nargs='?', help="输入的 Markdown 文件")
    parser.add_argument('-t', '--template', default='elegant', help="排版模板 (default: elegant)")
    parser.add_argument('-o', '--output', help="输出 HTML 文件路径")
    parser.add_argument('-l', '--list', action='store_true', help="列出所有可用模板")
    parser.add_argument('--preview', action='store_true', help="生成后预览 (打开 HTML 文件)")
    
    args = parser.parse_args()
    
    styler = WeChatStyler(template=args.template)
    
    # 列出模板
    if args.list:
        print("可用模板:")
        for t in styler.list_templates():
            marker = " ← 当前" if t == args.template else ""
            print(f"  • {t}{marker}")
        return
    
    # 需要输入文件
    if not args.input:
        parser.print_help()
        return
    
    # 转换
    try:
        html = styler.convert_file(args.input, args.output)
        
        # 预览
        if args.preview:
            output_path = args.output or str(Path(args.input).with_suffix('.html'))
            print(f"\n📱 生成的 HTML 已保存，可复制到微信公众号后台")
            print(f"   或者用浏览器打开预览: {output_path}")
            
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()