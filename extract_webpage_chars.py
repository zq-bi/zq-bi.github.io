#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網頁字符提取工具 - Extract characters from webpage
"""

import re
import os
from collections import Counter

def extract_chinese_chars(text):
    """提取中文字符"""
    # 匹配中文字符的正則表達式
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3300-\u33ff\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\u2ceb0-\u2ebef\u30000-\u3134f\u31350-\u323af]')
    return chinese_pattern.findall(text)

def extract_latin_chars(text):
    """提取拉丁字母和數字"""
    # 匹配拉丁字母、數字和常用符號
    latin_pattern = re.compile(r'[a-zA-Z0-9\s.,!?;:()\[\]{}"\'-+=/\\|@#$%^&*~`]')
    return latin_pattern.findall(text)

def extract_symbols(text):
    """提取特殊符號"""
    # 匹配中文標點符號和其他特殊符號
    symbol_pattern = re.compile(r'[，。！？；：（）【】「」『』—…·《》〈〉【】〖〗〓□■●◆◇○◎△▲※→←↑↓↖↗↘↙]')
    return symbol_pattern.findall(text)

def read_html_file(file_path):
    """讀取 HTML 文件內容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"讀取文件 {file_path} 時發生錯誤: {e}")
        return ""

def analyze_html_content(html_content):
    """分析 HTML 內容，提取所有字符"""
    # 移除 HTML 標籤，只保留文本內容
    text_content = re.sub(r'<[^>]+>', '', html_content)
    
    # 提取各種字符
    chinese_chars = extract_chinese_chars(text_content)
    latin_chars = extract_latin_chars(text_content)
    symbols = extract_symbols(text_content)
    
    # 統計字符頻率
    chinese_counter = Counter(chinese_chars)
    latin_counter = Counter(latin_chars)
    symbols_counter = Counter(symbols)
    
    return {
        'chinese': chinese_chars,
        'latin': latin_chars,
        'symbols': symbols,
        'chinese_counter': chinese_counter,
        'latin_counter': latin_counter,
        'symbols_counter': symbols_counter
    }

def create_comprehensive_subset(input_font, output_dir, all_chars, subset_name="comprehensive"):
    """創建包含所有字符的綜合字體子集"""
    try:
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 輸出文件名
        output_file = os.path.join(output_dir, f"JingHuaLaoSongTi_{subset_name}.woff2")
        
        # 創建臨時文本文件
        temp_text_file = f"temp_{subset_name}.txt"
        with open(temp_text_file, 'w', encoding='utf-8') as f:
            f.write(''.join(all_chars))
        
        print(f"正在創建綜合字體子集...")
        print(f"包含字符數量: {len(all_chars)}")
        print(f"輸出文件: {output_file}")
        
        # 使用 fonttools 進行字體子集化
        import subprocess
        import sys
        import time
        
        cmd = [
            sys.executable, "-m", "fontTools.subset",
            input_font,
            f"--text-file={temp_text_file}",
            f"--output-file={output_file}",
            "--flavor=woff2",
            "--layout-features=*"
        ]
        
        print(f"執行命令: {' '.join(cmd)}")
        
        # 添加超時控制
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)  # 15分鐘超時
        
        # 清理臨時文件
        if os.path.exists(temp_text_file):
            os.remove(temp_text_file)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            elapsed_time = time.time() - start_time
            print(f"✓ 成功創建 {output_file} ({file_size:,} bytes) - 耗時 {elapsed_time:.2f}秒")
            return True
        else:
            print(f"✗ 處理失敗:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ 處理超時 (超過15分鐘)")
        return False
    except Exception as e:
        print(f"✗ 處理時發生錯誤: {e}")
        return False

def create_css_file(output_dir, subset_name="comprehensive"):
    """創建 CSS 文件"""
    css_content = f"""/* 綜合字體子集 CSS */
/* 包含網頁中所有使用字符的字體文件 */

@font-face {{
    font-family: 'JingHuaLaoSongTi';
    src: url('./JingHuaLaoSongTi_{subset_name}.woff2') format('woff2');
    font-display: swap;
}}

"""
    
    css_file = os.path.join(output_dir, "font-comprehensive.css")
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✓ 創建 CSS 文件: {css_file}")

def main():
    """主函數"""
    print("=== 網頁字符提取工具 ===")
    print()
    
    # 檢查輸入文件
    input_font = "JingHuaLaoSongTi_v2.002.woff2"
    html_file = "index.html"
    
    if not os.path.exists(input_font):
        print(f"錯誤: 找不到字體文件 {input_font}")
        return
    
    if not os.path.exists(html_file):
        print(f"錯誤: 找不到 HTML 文件 {html_file}")
        return
    
    print(f"分析 HTML 文件: {html_file}")
    print(f"字體文件: {input_font}")
    print()
    
    # 讀取 HTML 內容
    html_content = read_html_file(html_file)
    if not html_content:
        return
    
    # 分析字符
    analysis = analyze_html_content(html_content)
    
    # 顯示統計結果
    print("=== 字符統計結果 ===")
    print(f"中文字符數量: {len(analysis['chinese'])}")
    print(f"拉丁字符數量: {len(analysis['latin'])}")
    print(f"符號數量: {len(analysis['symbols'])}")
    print()
    
    # 顯示中文字符
    chinese_chars = sorted(set(analysis['chinese']))
    print(f"中文字符列表 ({len(chinese_chars)} 個):")
    print(''.join(chinese_chars))
    print()
    
    # 顯示字符頻率（前20個）
    print("中文字符頻率 (前20個):")
    for char, count in analysis['chinese_counter'].most_common(20):
        print(f"  {char}: {count}")
    print()
    
    # 合併所有字符
    all_chars = list(set(analysis['chinese'] + analysis['latin'] + analysis['symbols']))
    print(f"總字符數量: {len(all_chars)}")
    print()
    
    # 創建綜合字體子集
    output_dir = "font-subsets"
    if create_comprehensive_subset(input_font, output_dir, all_chars):
        create_css_file(output_dir)
        
        print()
        print("=== 處理完成 ===")
        print("已創建包含所有網頁字符的綜合字體子集")
        print("使用方法:")
        print("1. 在 HTML 中引入 font-comprehensive.css")
        print("2. 使用 font-family: 'JingHuaLaoSongTi' 來應用字體")
    else:
        print("字體子集創建失敗")

if __name__ == "__main__":
    main() 