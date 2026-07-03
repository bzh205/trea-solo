"""电商价格采集对比 - CLI 工具"""
import argparse
import asyncio
import json
import sys
import os

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import PriceCompareEngine


PLATFORM_NAMES = {"jd": "京东", "taobao": "淘宝", "pdd": "拼多多"}
LABEL_ICONS = {
    "强烈推荐": "★★★",
    "推荐": "★★☆",
    "一般": "★☆☆",
    "不推荐": "☆☆☆",
}


def print_table(products: list, recommendations: list):
    """打印商品价格对比表格"""
    if not products:
        print("\n未找到任何商品数据")
        return

    # 表头
    print("\n" + "=" * 100)
    print(f"{'序号':<4} {'平台':<6} {'商品名称':<32} {'价格':>8} {'销量':>10} {'评分':>5} {'推荐':>8}")
    print("-" * 100)

    # 构建推荐标签映射
    label_map = {}
    for rec in recommendations:
        label_map[rec["title"]] = rec.get("recommend_label", "")

    for i, p in enumerate(products, 1):
        title = p["title"][:28] + "..." if len(p["title"]) > 28 else p["title"]
        platform = PLATFORM_NAMES.get(p["platform"], p["platform"])
        price = f"¥{p['price']:.2f}"
        sales = _format_sales(p["sales"])
        score = f"{p['shop_score']:.1f}"
        label = label_map.get(p["title"], "")
        icon = LABEL_ICONS.get(label, "")

        print(f"{i:<4} {platform:<6} {title:<32} {price:>8} {sales:>10} {score:>5} {icon:>5} {label}")

    print("=" * 100)


def print_summary(comparison: dict):
    """打印汇总信息"""
    summary = comparison.get("summary", {})
    if not summary:
        return

    print(f"\n{'='*50}")
    print(f"  采集汇总")
    print(f"{'='*50}")
    print(f"  商品总数: {summary.get('total_count', 0)}")
    print(f"  最低价格: ¥{summary.get('min_price', 0):.2f}")
    print(f"  最高价格: ¥{summary.get('max_price', 0):.2f}")
    print(f"  平均价格: ¥{summary.get('avg_price', 0):.2f}")
    platforms = [PLATFORM_NAMES.get(p, p) for p in summary.get("platforms", [])]
    print(f"  采集平台: {', '.join(platforms)}")

    # 平台对比
    plat_stats = comparison.get("platform_comparison", [])
    if plat_stats:
        print(f"\n  {'平台':<6} {'数量':>4} {'最低价':>8} {'最高价':>8} {'均价':>8} {'均销量':>10} {'均评分':>6}")
        print(f"  {'-'*56}")
        for s in plat_stats:
            plat = PLATFORM_NAMES.get(s["platform"], s["platform"])
            print(f"  {plat:<6} {s['count']:>4} ¥{s['min_price']:<7.2f} ¥{s['max_price']:<7.2f} ¥{s['avg_price']:<7.2f} {s['avg_sales']:>10} {s['avg_score']:>5.2f}")

    # 最佳性价比
    best = comparison.get("best_deals", [])
    if best:
        print(f"\n  性价比 TOP5:")
        for i, d in enumerate(best, 1):
            plat = PLATFORM_NAMES.get(d["platform"], d["platform"])
            print(f"  {i}. [{plat}] {d['title'][:30]} ¥{d['price']:.2f} (性价比分: {d['value_score']})")

    print(f"{'='*50}")


def _format_sales(sales: int) -> str:
    if sales >= 10000:
        return f"{sales / 10000:.1f}万+"
    return str(sales)


def main():
    parser = argparse.ArgumentParser(
        description="电商商品价格采集与对比工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py search "蓝牙耳机"
  python cli.py search "蓝牙耳机" --platforms jd,taobao
  python cli.py search "蓝牙耳机" --max-items 10 --output result.json
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索并对比商品价格")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument(
        "--platforms", default="jd,taobao,pdd", help="平台列表，逗号分隔 (默认: jd,taobao,pdd)"
    )
    search_parser.add_argument("--max-items", type=int, default=20, help="每平台最大采集数 (默认: 20)")
    search_parser.add_argument("--output", "-o", help="输出JSON文件路径")
    search_parser.add_argument("--no-headless", action="store_true", help="显示浏览器窗口（调试用）")

    # demo 命令（使用示例数据）
    demo_parser = subparsers.add_parser("demo", help="使用示例数据演示")

    args = parser.parse_args()

    if args.command == "demo":
        _run_demo()
        return

    if args.command != "search":
        parser.print_help()
        return

    platforms = [p.strip() for p in args.platforms.split(",")]
    print(f"\n正在从 {', '.join(PLATFORM_NAMES.get(p, p) for p in platforms)} 采集「{args.keyword}」...")
    print("请稍候，首次运行可能需要安装浏览器...\n")

    engine = PriceCompareEngine(headless=not args.no_headless)
    result = asyncio.run(engine.run(args.keyword, platforms, args.max_items))

    # 打印模拟数据提示
    if result.get("is_simulated"):
        print(f"\n{'='*80}")
        print("  【提示】", result.get("note", ""))
        print(f"{'='*80}\n")

    # 打印结果
    print_table(result["products"], result["recommendations"])
    print_summary(result["comparison"])

    # 输出文件
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


def _run_demo():
    """使用示例数据演示"""
    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_results.json")
    if not os.path.exists(demo_path):
        print("示例数据文件不存在")
        return
    with open(demo_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    print_table(result["products"], result["recommendations"])
    print_summary(result["comparison"])


if __name__ == "__main__":
    main()
