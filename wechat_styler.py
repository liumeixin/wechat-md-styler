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
        
        # 0. 去除 frontmatter (--- ... ---)
        html = re.sub(r'^---\n[\s\S]*?\n---\n', '', html)
        
        # 0.1 图片处理必须最先（优先于标题、代码块等）
        html = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'<img referrerpolicy="no-referrer" src="\2" alt="\1" title="" style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; display: block; margin: 8px auto; max-width: 100%;">',
            html
        )
        
        # 1. 代码块 ```...```
        html = re.sub(
            r'```(\w*)\n(.*?)```',
            r'<pre style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; overflow-wrap: break-word; padding: 12px 16px; border-radius: 4px; margin: 12px 0px; background: rgb(248, 248, 248); overflow-x: auto;"><code class="language-\1" style="font-size: inherit; line-height: inherit; overflow-wrap: break-word; padding: 0px; margin: 0px; color: rgb(51, 51, 51);">\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # 2. 行内代码 `...` - 橙色 + 灰底
        html = re.sub(
            r'`([^`]+)`',
            r'<code style="font-size: inherit; line-height: inherit; overflow-wrap: break-word; padding: 2px 4px; border-radius: 4px; margin: 0px 2px; color: rgb(145, 109, 213); background: rgb(248, 248, 248);">\1</code>',
            html
        )
        
        # 3. 标题处理
        lines = html.split('\n')
        new_lines = []
        
        for line in lines:
            # H1: # 标题
            if line.startswith('# '):
                new_lines.append(f'<h1 style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0.5em 0px; font-weight: bold;">{line[2:]}</h1>')
            # H2: ## 标题 - 居中 + 紫色下划线
            elif line.startswith('## '):
                new_lines.append(f'<h2 style="text-align: center; font-size: 20px; color: rgb(80, 80, 80); margin: 1em auto; font-weight: bold;"><span style="display: inline-block; border-bottom: 2px solid rgb(176, 159, 218); padding-bottom: 8px;">{line[3:]}</span></h2>')
            # H3: ### 标题 - 居中 + 紫色下划线
            elif line.startswith('### '):
                title_text = line[4:]
                new_lines.append(f'<h3 style="text-align: center; font-size: 18px; color: rgb(80, 80, 80); margin: 1em auto; font-weight: bold;"><span style="display: inline-block; border-bottom: 2px solid rgb(176, 159, 218); padding-bottom: 8px;">{title_text}</span></h3>')
            # H4: #### 标题 - 蓝色 + 竖线格式
            elif line.startswith('#### '):
                # 提取标题文字
                title_text = line[5:]
                # 如果用户已经写了 | ，就不再加；没有就自动加
                if '|' in title_text:
                    # 用户已写 | ，保持原样只加蓝色
                    new_lines.append(f'<h4 id="hspanstylecolor4169e1span" style="color: inherit; line-height: inherit; padding: 0px; margin: 0.5em 0px; font-weight: bold; font-size: 1.2em;"><span style="font-size: inherit; color: inherit; line-height: inherit; margin: 0px; padding: 0px;"><span style="font-size: inherit; line-height: inherit; margin: 0px; padding: 0px; color: #4169E1;">{title_text}</span></span></h4>')
                else:
                    # 自动加竖线
                    new_lines.append(f'<h4 id="hspanstylecolor4169e1span" style="color: inherit; line-height: inherit; padding: 0px; margin: 0.5em 0px; font-weight: bold; font-size: 1.2em;"><span style="font-size: inherit; color: inherit; line-height: inherit; margin: 0px; padding: 0px;"><span style="font-size: inherit; line-height: inherit; margin: 0px; padding: 0px; color: #4169E1;">| {title_text}</span></span></h4>')
            # 分割线
            elif re.match(r'^---+$', line) or re.match(r'^\*\*\*+$', line):
                new_lines.append('<hr>')
            # 空行：保留为空行
            elif not line.strip():
                new_lines.append('')
            # 普通段落
            else:
                new_lines.append(line)
        
        html = '\n'.join(new_lines)
        
        # 4.1 引用块 > text（必须先于段落处理）
        def process_blockquote(m):
            lines = m.group(1).strip().split('\n')
            content = '<br>'.join(line.strip() for line in lines if line.strip())
            return f'<blockquote style="line-height: inherit; display: block; padding: 15px 15px 15px 1rem; font-size: 0.9em; margin: 1em 0px; color: rgb(129, 145, 152); border-left: 6px solid rgb(220, 230, 240); background: rgb(242, 247, 251); overflow: auto; overflow-wrap: normal; word-break: normal;"><p style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px;">{content}</p></blockquote>'
        
        html = re.sub(r'^> (.+)$', process_blockquote, html, flags=re.MULTILINE)
        
        # 4. 强调 **粗体** 或 __粗体__
        html = re.sub(
            r'\*\*([^*]+)\*\*',
            r'<strong style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px;">\1</strong>',
            html
        )
        html = re.sub(
            r'__([^_]+)__',
            r'<strong style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px;">\1</strong>',
            html
        )
        
        # 5. 斜体 *斜体* 或 _斜体_
        html = re.sub(
            r'\*([^*]+)\*',
            r'<em style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px;">\1</em>',
            html
        )
        
        # 6. 链接 [文字](url)
        html = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px; text-decoration: none; border-bottom: 1px solid rgb(145, 109, 213);">\1</a>',
            html
        )
        
        # 7. 无序列表
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
        
        # 10. 段落处理：将连续的文本块包裹为 p（带内联样式）
        # 注意：引用块已在 markdown_to_html 阶段处理，这里不再重复处理
        paragraphs = []
        in_list = False
        in_pre = False
        
        for line in html.split('\n'):
            line = line.strip()
            
            # 空行：转为空的 <p> 标签，让光标可以停在空行处
            if not line:
                if in_list:
                    paragraphs.append('</ul>')
                    in_list = False
                paragraphs.append('<p>&nbsp;</p>')
                continue
            
            # 代码块（<pre>开头）才特殊处理，行内<code>不处理
            if line.startswith('<pre>'):
                in_pre = True
                paragraphs.append(line)
            elif in_pre:
                paragraphs.append(line)
                if '</pre>' in line:
                    in_pre = False
            # 列表项
            elif line.startswith('<li>'):
                if not in_list:
                    paragraphs.append('<ul style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 12px 0px; padding-left: 24px;">')
                    in_list = True
                paragraphs.append(line)
            # 标题
            elif line.startswith('<h'):
                paragraphs.append(line)
            # 分割线
            elif line == '<hr>':
                paragraphs.append('<hr style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; height: 1px; margin: 1.5rem 0px; border-width: 1px medium medium; border-style: dashed none none; border-color: rgb(165, 165, 165) currentcolor currentcolor; border-image: initial;">')
            # 图片单独成行（不再使用figure标签，改为直接检查img标签）
            elif line.startswith('<img '):
                paragraphs.append(line)
            # 其他作为段落
            else:
                if in_list:
                    paragraphs.append('</ul>')
                    in_list = False
                paragraphs.append(f'<p style="font-size: inherit; color: inherit; line-height: inherit; padding: 0px; margin: 0px;">{line}</p>')
        
        if in_list:
            paragraphs.append('</ul>')
        
        return '\n'.join(paragraphs) + '\n\n'
    
    def _wrap_html(self, content: str) -> str:
        """包装成微信公众号可用的纯内联样式（抄自mdnice）"""
        
        # PNG方格子pattern（使用135editor代理域名，微信白名单）
        grid_png = "http://image2.135editor.com/cache/remote/aHR0cHM6Ly9tbWJpei5xcGljLmNuL21tYml6X3BuZy9mZ25reGZHbm5rVGRKVFFpYWpiaWNSWUVuOGxGYWs1QXpuZ01kY2R4WkZjdWZOcTRKaWJRZThHOHhnTTdYWVNnZmdJMERqR2w2dDZhZHh5SXZNUU5pY0Z4aWJpY0EvNjQwP3d4X2ZtdD1wbmc="
        
        # 根section样式
        root_style = (
            'margin: 0px; '
            'padding: 10px; '
            'background-color: #FFF; '
            f'background-image: url("{grid_png}"); '
            'background-repeat: repeat; '
            'background-size: auto; '
            'background-position: center center; '
            'width: auto; '
            'font-family: "Georgia", "Times New Roman", "Microsoft YaHei", "PingFangSC-regular", serif; '
            'font-size: 16px; '
            'color: rgb(0, 0, 0); '
            'line-height: 1.5em; '
            'word-spacing: 0em; '
            'letter-spacing: 0em; '
            'word-break: break-word; '
            'overflow-wrap: break-word; '
            'text-align: left; '
            'box-sizing: border-box; '
            'overflow-x: hidden; '
        )
        
        # 处理段落之间的换行
        lines = content.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            processed_lines.append(line)
        
        compact_content = '\n'.join(processed_lines)
        
        # 返回纯section标签（不用class，微信公众号只认内联样式）
        return f'<section data-tool="wechat-styler" style="{root_style}">{compact_content}</section>'
    
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