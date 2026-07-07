# -*- coding: utf-8 -*-
"""统一的文件读写工具模块。

提供基于脚本位置的路径推算、YAML/CSV/JSON 读写，
以及训练资源（音频、模板、参考索引）的便捷访问接口。
所有路径均基于 pathlib.Path 计算，支持跨平台。
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# pyyaml 可选依赖：若未安装则提供简易 YAML 解析回退
# ---------------------------------------------------------------------------
try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ---------------------------------------------------------------------------
# 路径定位
# ---------------------------------------------------------------------------

# 当前文件所在目录（common/）
_CURRENT_DIR: Path = Path(__file__).parent.resolve()

# scripts 目录（common/ 的上级）
_SCRIPTS_DIR: Path = _CURRENT_DIR.parent

# shooting-training-scale 根目录（scripts/ 的上级）
_SCALE_ROOT: Path = _SCRIPTS_DIR.parent

# assets 目录（scale 根目录下的 assets/）
_ASSETS_DIR: Path = _SCALE_ROOT / "assets"


def get_assets_dir() -> Path:
    """返回 assets 目录的绝对路径。

    Returns:
        Path: assets 目录的绝对路径对象。
    """
    return _ASSETS_DIR


def get_scripts_dir() -> Path:
    """返回 scripts 目录的绝对路径。

    Returns:
        Path: scripts 目录的绝对路径对象。
    """
    return _SCRIPTS_DIR


# ---------------------------------------------------------------------------
# YAML 读写
# ---------------------------------------------------------------------------

def _simple_yaml_load(text: str) -> Dict[str, Any]:
    """简易 YAML 解析器（仅在 pyyaml 不可用时作为回退）。

    仅支持简单的 key: value 层级结构，不支持多行、锚点等高级特性。

    Args:
        text: YAML 文件的原始文本内容。

    Returns:
        解析后的字典。
    """
    result: Dict[str, Any] = {}
    current_section: Optional[str] = None

    for line in text.splitlines():
        stripped = line.strip()
        # 跳过空行和注释
        if not stripped or stripped.startswith("#"):
            continue

        # 简单顶层键值对
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            # 去除引号
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            # 尝试数值转换
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    if val.lower() in ("true", "yes"):
                        val = True
                    elif val.lower() in ("false", "no"):
                        val = False
                    elif val.lower() in ("null", "~", ""):
                        val = None
            result[key] = val

    return result


def load_yaml(filepath: str | Path, subdir: str | None = None) -> Dict[str, Any]:
    """读取 YAML 文件并返回字典。

    优先使用 pyyaml，若不可用则回退到内置简易解析器。

    Args:
        filepath: YAML 文件名或路径。若为文件名且 subdir 不为 None，则自动拼接
                 get_assets_dir() / subdir / filepath。
        subdir: 相对于 assets 的子目录（如 "config-rules"、"tables"）。

    Returns:
        解析后的字典。
    """
    filepath = Path(filepath)
    if subdir and not filepath.is_absolute() and not filepath.exists():
        filepath = get_assets_dir() / subdir / filepath
    if not filepath.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {filepath}")

    text = filepath.read_text(encoding="utf-8")

    if _HAS_YAML:
        return yaml.safe_load(text) or {}
    else:
        print("[警告] pyyaml 未安装，使用简易 YAML 解析器，仅支持简单键值对。")
        return _simple_yaml_load(text)


# ---------------------------------------------------------------------------
# CSV 读写
# ---------------------------------------------------------------------------

def load_csv(filepath: str | Path, subdir: str | None = None) -> List[Dict[str, str]]:
    """读取 CSV 文件，返回字典列表（每行一个字典，键为表头）。

    Args:
        filepath: CSV 文件名或路径。若为文件名且 subdir 不为 None，则自动拼接。
        subdir: 相对于 assets 的子目录。

    Returns:
        字典列表，每个字典代表 CSV 中的一行。
    """
    filepath = Path(filepath)
    if subdir and not filepath.is_absolute() and not filepath.exists():
        filepath = get_assets_dir() / subdir / filepath
    if not filepath.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {filepath}")

    with filepath.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------------------------------
# JSON 读写
# ---------------------------------------------------------------------------

def load_json(filepath: str | Path, subdir: str | None = None) -> Dict[str, Any]:
    """读取 JSON 文件并返回字典。

    Args:
        filepath: JSON 文件名或路径。若为文件名且 subdir 不为 None，则自动拼接。
        subdir: 相对于 assets 的子目录。

    Returns:
        解析后的字典。
    """
    filepath = Path(filepath)
    if subdir and not filepath.is_absolute() and not filepath.exists():
        filepath = get_assets_dir() / subdir / filepath
    if not filepath.exists():
        raise FileNotFoundError(f"JSON 文件不存在: {filepath}")

    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: str | Path) -> None:
    """将字典保存为 JSON 文件。

    Args:
        data: 要保存的字典数据。
        filepath: 输出 JSON 文件的路径。
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 业务快捷方法
# ---------------------------------------------------------------------------

def load_reference_index() -> List[Dict[str, str]]:
    """读取 references/reference-index.csv，返回参考索引列表。

    Returns:
        参考索引的字典列表。若文件不存在则返回空列表。
    """
    ref_path = _SCALE_ROOT / "references" / "reference-index.csv"
    if not ref_path.exists():
        print(f"[警告] 参考索引文件不存在: {ref_path}")
        return []
    return load_csv(ref_path)


def list_audio_files(subdir: str) -> List[Path]:
    """列出 audio-material/ 下指定子目录的所有 wav/mp3 文件。

    Args:
        subdir: audio-material/ 下的子目录名称，如 "warm-up"。

    Returns:
        匹配到的音频文件路径列表（按文件名排序）。
    """
    audio_dir = _ASSETS_DIR / "audio-material" / subdir
    if not audio_dir.exists():
        print(f"[警告] 音频目录不存在: {audio_dir}")
        return []

    extensions = {".wav", ".mp3", ".WAV", ".MP3"}
    files = sorted(
        [f for f in audio_dir.iterdir() if f.is_file() and f.suffix in extensions]
    )
    return files


def find_template(template_name: str) -> Optional[Path]:
    """在 assets/templates/ 下查找模板文件。

    支持传入带或不带扩展名的模板名称。若未指定扩展名，
    则依次尝试 .md 和 .docx。

    Args:
        template_name: 模板文件名称，如 "report-template" 或 "report-template.md"。

    Returns:
        找到的模板文件路径；若未找到则返回 None。
    """
    template_dir = _ASSETS_DIR / "templates"

    # 如果已带扩展名，直接查找
    candidate = template_dir / template_name
    if candidate.exists():
        return candidate

    # 依次尝试常见扩展名
    for ext in (".md", ".docx", ".txt"):
        candidate = template_dir / f"{template_name}{ext}"
        if candidate.exists():
            return candidate

    print(f"[警告] 未找到模板文件: {template_name}（在 {template_dir} 中）")
    return None


# ---------------------------------------------------------------------------
# 测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("file_io.py 模块测试")
    print("=" * 60)

    # 1. 路径测试
    print(f"\n[1] get_assets_dir()  = {get_assets_dir()}")
    print(f"    get_scripts_dir() = {get_scripts_dir()}")
    print(f"    路径存在: assets={get_assets_dir().exists()}, scripts={get_scripts_dir().exists()}")

    # 2. 参考索引测试
    print(f"\n[2] load_reference_index()")
    ref_index = load_reference_index()
    print(f"    参考索引条数: {len(ref_index)}")
    if ref_index:
        print(f"    第一条: {ref_index[0]}")

    # 3. 音频文件列表测试
    print(f"\n[3] list_audio_files('warm-up')")
    audio_files = list_audio_files("warm-up")
    print(f"    找到 {len(audio_files)} 个音频文件")
    for af in audio_files[:5]:
        print(f"    - {af.name}")

    # 4. 模板查找测试
    print(f"\n[4] find_template('report-template')")
    tpl = find_template("report-template")
    print(f"    查找结果: {tpl}")

    # 5. JSON 保存/读取测试（临时文件）
    print(f"\n[5] JSON 保存/读取测试")
    test_data = {"test": "文件读写测试", "value": 42}
    test_json_path = _CURRENT_DIR / "_test_temp.json"
    save_json(test_data, test_json_path)
    loaded = load_json(test_json_path)
    print(f"    保存: {test_data}")
    print(f"    读取: {loaded}")
    assert loaded == test_data, "JSON 读写不一致!"
    print("    JSON 读写测试通过")
    test_json_path.unlink(missing_ok=True)

    # 6. YAML 加载测试
    print(f"\n[6] load_yaml 测试")
    print(f"    pyyaml 可用: {_HAS_YAML}")

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
