#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字體分塊工具 - Font Subsetting Tool
參考掘金文章: https://juejin.cn/post/7490820182102671398
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def install_dependencies():
    """安裝必要的依賴包"""
    try:
        import fonttools
        print("fonttools 已安裝")
    except ImportError:
        print("正在安裝 fonttools...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "fonttools"
        ])
    
    try:
        import brotli
        print("brotli 已安裝")
    except ImportError:
        print("正在安裝 brotli...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "brotli"
        ])

def get_unicode_ranges():
    """定義 Unicode 字符範圍 - 簡化版本"""
    ranges = {
        "basic_latin": (0x0020, 0x007F),      # 基本拉丁字母
        "latin_extended": (0x00A0, 0x00FF),   # 拉丁擴展
        "cjk_basic": (0x4E00, 0x9FFF),        # 中日韓統一表意文字（基本）
        "cjk_symbols": (0x3000, 0x303F),      # 中日韓符號和標點
        "cjk_radicals": (0x2E80, 0x2EFF),     # 中日韓部首補充
    }
    return ranges

def create_subset_font(input_font, output_dir, unicode_range, range_name):
    """創建字體子集"""
    try:
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成字符範圍字符串
        start, end = unicode_range
        char_range = f"U+{start:04X}-{end:04X}"
        
        # 輸出文件名
        output_file = os.path.join(output_dir, f"JingHuaLaoSongTi_{range_name}.woff2")
        
        print(f"正在處理 {range_name} ({char_range})...")
        print(f"輸入文件: {input_font}")
        print(f"輸出文件: {output_file}")
        
        # 使用 fonttools 進行字體子集化
        cmd = [
            sys.executable, "-m", "fontTools.subset",
            input_font,
            f"--unicodes={char_range}",
            f"--output-file={output_file}",
            "--flavor=woff2",
            "--layout-features=*",
            "--no-hinting",
            "--verbose"
        ]
        
        print(f"執行命令: {' '.join(cmd)}")
        
        # 添加超時控制
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分鐘超時
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            elapsed_time = time.time() - start_time
            print(f"✓ 成功創建 {output_file} ({file_size:,} bytes) - 耗時 {elapsed_time:.2f}秒")
            return True
        else:
            print(f"✗ 處理 {range_name} 失敗:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ 處理 {range_name} 超時 (超過5分鐘)")
        return False
    except Exception as e:
        print(f"✗ 處理 {range_name} 時發生錯誤: {e}")
        return False

def create_css_file(output_dir, ranges):
    """創建 CSS 文件用於字體加載"""
    css_content = """/* 字體分塊 CSS */
/* 自動生成的字體加載文件 */

"""
    
    for range_name, (start, end) in ranges.items():
        font_file = f"JingHuaLaoSongTi_{range_name}.woff2"
        css_content += f"""@font-face {{
    font-family: 'JingHuaLaoSongTi';
    src: url('./{font_file}') format('woff2');
    unicode-range: U+{start:04X}-{end:04X};
    font-display: swap;
}}

"""
    
    css_file = os.path.join(output_dir, "font-subset.css")
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✓ 創建 CSS 文件: {css_file}")

def test_font_file(input_font):
    """測試字體文件是否可用"""
    try:
        cmd = [
            sys.executable, "-m", "fontTools.ttx",
            "-l", input_font
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✓ 字體文件檢查通過")
            return True
        else:
            print("✗ 字體文件檢查失敗:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ 字體文件檢查錯誤: {e}")
        return False

def main():
    """主函數"""
    print("=== 字體分塊工具 ===")
    print("參考: https://juejin.cn/post/7490820182102671398")
    print()
    
    # 檢查輸入文件
    input_font = "JingHuaLaoSongTi_v2.002.woff2"
    if not os.path.exists(input_font):
        print(f"錯誤: 找不到字體文件 {input_font}")
        return
    
    print(f"字體文件大小: {os.path.getsize(input_font):,} bytes")
    
    # 安裝依賴
    install_dependencies()
    
    # 測試字體文件
    if not test_font_file(input_font):
        print("字體文件可能有問題，但繼續嘗試...")
    
    # 創建輸出目錄
    output_dir = "font-subsets"
    
    # 獲取 Unicode 範圍
    ranges = get_unicode_ranges()
    
    print(f"開始處理字體文件: {input_font}")
    print(f"輸出目錄: {output_dir}")
    print(f"將創建 {len(ranges)} 個字體子集")
    print()
    
    # 處理每個範圍
    success_count = 0
    for range_name, unicode_range in ranges.items():
        if create_subset_font(input_font, output_dir, unicode_range, range_name):
            success_count += 1
        else:
            print(f"跳過 {range_name}，繼續下一個...")
    
    # 創建 CSS 文件
    create_css_file(output_dir, ranges)
    
    print()
    print(f"=== 處理完成 ===")
    print(f"成功創建 {success_count}/{len(ranges)} 個字體子集")
    print(f"CSS 文件已生成: {output_dir}/font-subset.css")
    print()
    print("使用方法:")
    print("1. 將 font-subsets 目錄中的所有文件上傳到您的網站")
    print("2. 在 HTML 中引入 font-subset.css")
    print("3. 使用 font-family: 'JingHuaLaoSongTi' 來應用字體")

if __name__ == "__main__":
    main() 