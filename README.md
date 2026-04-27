# 微信公众号 Markdown 排版工具

[![Build and Push Docker Image](https://github.com/liumeixin/wechat-md-styler/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/liumeixin/wechat-md-styler/actions/workflows/docker-publish.yml)
[![Docker Image Size](https://img.shields.io/docker/image-size/ghcr.io/liumeixin/wechat-md-styler/latest)](https://github.com/liumeixin/wechat-md-styler/pkgs/container/wechat-md-styler)

将 Markdown 文件转换为微信公众号可用的 HTML 格式，支持多套模板， 提供交互式网页界面。

## 功能特性

- 🎨 **多模板** - 5 套预设模板可选
- 📱 **微信优化** - 针对微信公众号的 CSS 优化
- 🔧 **可扩展** - 轻松添加新模板
- 📝 **交互式网页** - 实时预览 + 一键复制
- 🐳 **Docker 部署** - 支持自动构建镜像

## 快速开始

### Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/wechat-md-styler.git
cd wechat-md-styler

# 2. 构建并启动
docker-compose up -d

# 3. 访问
# http://your-nas-ip:18888
```

或直接拉取镜像（推送代码后自动构建）:

```bash
docker pull ghcr.io/你的用户名/wechat-md-styler:latest
docker run -d -p 18888:8080 --name wechat-styler ghcr.io/你的用户名/wechat-md-styler:latest
```

### 本地运行

```bash
pip install flask pyyaml
python app.py
# 访问 http://localhost:8080
```

### 命令行转换

```bash
python wechat_styler.py your-article.md -t elegant -o output.html
```

## 可用模板

| 模板 | 风格 | 预览 |
|------|------|------|
| `elegant` | 优雅紫（默认） | 参考 Hermes 那篇文章 |
| `tech` | 科技蓝 | 适合技术文章 |
| `minimal` | 简约白 | 干净简洁 |
| `warm` | 暖色调 | 适合生活类 |
| `dark` | 暗夜模式 | 深色主题 |

## 微信公众号使用

1. 访问网页工具
2. 输入 Markdown 内容
3. 选择模板（顶部按钮切换）
4. 点击"一键复制"
5. 粘贴到微信公众号后台

## 添加新模板

1. 在 `templates/` 目录创建新的 CSS 文件，如 `mytheme.css`
2. 重启服务即可自动识别

## 项目结构

```
wechat-md-styler/
├── .github/workflows/    # GitHub Actions 自动构建
│   └── docker-publish.yml
├── Dockerfile             # Docker 镜像定义
├── docker-compose.yml     # 部署配置
├── app.py                 # Flask 网页应用
├── wechat_styler.py       # 核心转换器
├── config.yaml            # 模板配置
├── templates/             # CSS 模板
│   ├── elegant.css        # 优雅紫
│   ├── tech.css           # 科技蓝
│   ├── minimal.css        # 简约白
│   ├── warm.css           # 暖色调
│   └── dark.css           # 暗夜
└── examples/              # 示例
    ├── test.md
    └── test.html
```

## 自动构建说明

推送到 GitHub 后会自动构建 Docker 镜像：

- 镜像地址：`ghcr.io/你的用户名/wechat-md-styler:latest`
- 触发条件：推送至 main 分支 或打 tag (如 v1.0.0)

## License

MIT