# 电商商品价格自动化采集与对比工具

支持从京东、淘宝、拼多多批量采集商品价格信息，自动清洗去重，按价格排序，包含横向对比、价格趋势图表和性价比推荐。

## 功能特性

- 多平台采集：京东、淘宝、拼多多（基于 Playwright 网页爬虫）
- 数据处理：自动清洗异常值、去重、按价格升序排序
- 智能分析：平台横向对比、性价比推荐标注（强烈推荐/推荐/一般/不推荐）
- 数据可视化：价格对比柱状图、价格区间分布、平台雷达图、占比饼图
- 双入口：CLI 命令行工具 + Web 演示页面

## 安装

```bash
cd price-compare
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### CLI 命令行工具

```bash
# 演示模式（使用示例数据）
python cli.py demo

# 真实采集
python cli.py search "蓝牙耳机"
python cli.py search "蓝牙耳机" --platforms jd,taobao --max-items 10
python cli.py search "蓝牙耳机" --output result.json
```

### Web 演示页面

```bash
python -m uvicorn interfaces.web.app:app --host 0.0.0.0 --port 8000
```

浏览器访问 http://localhost:8000

- 初始化展示示例数据（蓝牙耳机的采集结果）
- 输入关键词后可实时调用爬虫采集

## 项目结构

```
price-compare/
├── scrapers/          # 爬虫模块（基类 + 京东/淘宝/拼多多）
├── processors/        # 数据清洗 + 去重
├── analyzers/         # 对比 + 推荐 + 可视化数据生成
├── core/              # 引擎编排
├── interfaces/        # CLI + Web 接口层
├── models/            # 商品数据模型
├── utils/             # 辅助工具（UA轮换、延迟、文本处理）
├── data/              # 示例数据
└── cli.py             # CLI 入口
```

## 反爬策略

- 随机 User-Agent 轮换
- 请求间随机延迟 1-3 秒
- 无头浏览器 + 浏览器指纹模拟

## 性价比算法

综合分数 = 价格分数(0.4) + 销量分数(0.3) + 评分分数(0.3)
- 价格分数：越低越好（反向归一化）
- 推荐等级：≥0.8 强烈推荐，≥0.6 推荐，≥0.4 一般，<0.4 不推荐
