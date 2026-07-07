# -*- coding: utf-8 -*-
"""训练模块自动匹配参考文献 - Literature-Support-Agent

从 reference-index.csv 中匹配训练模块对应的参考文献，
支持按模块名、关键词匹配，以及全模块映射查询。
"""

import sys
import json
from pathlib import Path

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import load_csv, get_assets_dir


def _load_reference_index() -> list:
    """
    加载参考文献索引（带缓存）。
    """
    return load_csv(get_assets_dir().parent / "references" / "reference-index.csv")


def match_papers(training_module: str) -> list:
    """
    按训练模块名匹配参考文献。

    支持模糊匹配：模块名与「支撑业务模块」列做包含匹配。
    "支撑业务模块"列中用 "+" 分隔多个模块（如 "module1+module2"）。

    Args:
        training_module: 训练模块名
            支持：完整模块名（"module1-aimless-foundation"）或关键字（"心理训练"、"体能"）
            映射规则：
            - "module1" / "基础空枪定型" / "aimless" → module1 相关
            - "module2" / "实弹射击" / "live_fire" → module2 相关
            - "module3" / "体能" / "physical" → module3 相关
            - "module4" / "心理" / "mental" → module4 相关
            - "module5" / "装备" / "equipment" → module5 相关
            - "team" / "团队" → 团队保障相关

    Returns:
        匹配的参考文献列表 [{"编号", "文献名称", "作者/来源", "年份", "来源类型", "支撑业务模块", "对应智能体", "语言"}, ...]
    """
    index = _load_reference_index()
    module_lower = training_module.lower()

    # 模块名模糊匹配映射表
    alias_map = {
        "module1": ["module1"],
        "基础空枪定型": ["module1"],
        "aimless": ["module1"],
        "module2": ["module2"],
        "实弹射击": ["module2"],
        "live_fire": ["module2"],
        "module3": ["module3"],
        "体能": ["module3"],
        "physical": ["module3"],
        "module4": ["module4"],
        "心理": ["module4"],
        "mental": ["module4"],
        "module5": ["module5"],
        "装备": ["module5"],
        "equipment": ["module5"],
        "team": ["team"],
        "团队": ["team"],
        "data": ["data"],
        "数据": ["data"],
    }

    # 确定要匹配的模块关键字列表
    match_keys = []
    for alias, keys in alias_map.items():
        if alias in module_lower:
            match_keys.extend(keys)
            break

    # 如果模块名本身包含 "module"，也直接匹配
    if not match_keys:
        if "module" in module_lower:
            match_keys.append(module_lower)
        else:
            # 直接用输入关键字做模糊匹配
            match_keys.append(module_lower)

    results = []
    for paper in index:
        module_col = paper.get("支撑业务模块", "")
        module_col_lower = module_col.lower()
        for mk in match_keys:
            if mk in module_col_lower:
                results.append(paper)
                break

    return results


def match_by_keywords(keywords: list) -> list:
    """
    按关键词匹配文献（匹配文献名称、作者、支撑业务模块等多字段）。

    Args:
        keywords: 关键词列表 ["射击", "心理", "balance"]

    Returns:
        匹配的参考文献列表（去重）
    """
    index = _load_reference_index()
    results = []
    seen = set()

    for paper in index:
        # 在多个字段中搜索
        searchable = " ".join([
            paper.get("文献名称", ""),
            paper.get("作者/来源", ""),
            paper.get("支撑业务模块", ""),
            paper.get("对应智能体", ""),
        ]).lower()

        for kw in keywords:
            if kw.lower() in searchable:
                paper_id = paper.get("编号", "")
                if paper_id not in seen:
                    seen.add(paper_id)
                    results.append(paper)
                break

    return results


def get_all_modules_papers() -> dict:
    """
    返回所有训练模块对应的文献映射。

    Returns:
        {"module1": [参考文献列表], "module2": [...], ...}
    """
    index = _load_reference_index()

    # 提取所有唯一模块标识
    all_modules = set()
    for paper in index:
        module_col = paper.get("支撑业务模块", "")
        # "+" 分隔多模块
        parts = module_col.split("+")
        for p in parts:
            p = p.strip()
            if p:
                all_modules.add(p)

    # 为每个模块聚合文献
    result = {}
    for mod in sorted(all_modules):
        result[mod] = [paper for paper in index if mod.lower() in paper.get("支撑业务模块", "").lower()]

    return result


if __name__ == "__main__":
    # 演示调用：按模块名匹配
    print("=== match_papers('体能') ===")
    papers = match_papers("体能")
    for p in papers:
        print(f"  [{p.get('编号')}] {p.get('文献名称')} - {p.get('作者/来源')} ({p.get('年份')})")

    print("\n=== match_papers('module4') ===")
    papers4 = match_papers("module4")
    for p in papers4:
        print(f"  [{p.get('编号')}] {p.get('文献名称')} - {p.get('作者/来源')} ({p.get('年份')})")

    print("\n=== match_by_keywords(['shooting', '心理']) ===")
    kw_papers = match_by_keywords(["shooting", "心理"])
    for p in kw_papers:
        print(f"  [{p.get('编号')}] {p.get('文献名称')} ({p.get('语言')})")

    print("\n=== get_all_modules_papers() ===")
    all_map = get_all_modules_papers()
    for mod, refs in sorted(all_map.items()):
        print(f"  {mod}: {len(refs)} 篇文献")
