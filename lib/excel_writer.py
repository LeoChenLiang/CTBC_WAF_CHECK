# lib/excel_writer.py
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

def write_to_excel(data, output_file, sheet_name="WAF_Policy_list", columns=None):
    """將資料寫入Excel檔案，處理特定欄位的數字格式，並設置分頁名稱"""
    df = pd.DataFrame(data)
    # 將 Port 轉換為整數，忽略非數字的錯誤
    if "Port" in df.columns:
        df["Port"] = pd.to_numeric(df["Port"], errors='coerce').astype('Int64')
    # 如果有其他需要轉換為數字的欄位（如 Signature ID），可以添加
    # if "Signature ID" in df.columns:
    #     df["Signature ID"] = pd.to_numeric(df["Signature ID"], errors='coerce').astype('Int64')
    
    if columns:
        df = df[columns]  # 確保欄位順序與指定的 columns 一致
    
    # 使用 pandas 輸出到 Excel
    df.to_excel(output_file, sheet_name=sheet_name, index=False)
    print(f"已將結果輸出到 {output_file}，分頁名稱為 {sheet_name}")

def export_to_excel(results, output_file):
    """將解析結果輸出到 Excel 檔案"""
    data = []
    for file_path, virtuals in results.items():
        parts = Path(file_path).parts
        print(f"處理檔案路徑: {file_path}")
        print(f"路徑部分: {parts}")
        
        # 嘗試提取 host_name 根據新的路徑結構
        try:
            # 找到 file_input 目錄後的第一個子目錄（host_name 相關的部分）
            file_input_index = parts.index('file_input')
            if file_input_index + 1 < len(parts):
                folder_name_full = parts[file_input_index + 1]  # 例如 NH-IWEB-WAF-F5-1.ctbc.com_20241223
                print(f"找到 folder_name_full: {folder_name_full}")
                # 檢查 folder_name_full 是否符合預期格式
                if '-' in folder_name_full:
                    host_name = '-'.join(folder_name_full.split('-')[:3])  # 僅取 NH-IWEB-WAF-F5
                    print(f"提取的 host_name: {host_name}")
                else:
                    host_name = "Unknown"
                    print(f"警告：folder_name_full '{folder_name_full}' 不包含 '-'，設置為 Unknown")
            else:
                host_name = "Unknown"
                print(f"警告：'file_input' 後無有效目錄，設置為 Unknown")
        except ValueError:
            host_name = "Unknown"
            print(f"警告：路徑中未找到 'file_input' 目錄，設置為 Unknown")
        except Exception as e:
            host_name = "Unknown"
            print(f"錯誤：提取 host_name 時發生錯誤 {e}，設置為 Unknown")
        
        partition_name = Path(file_path).parent.name  # 例如 INPG
        
        for v in virtuals:
            data.append({
                'Host Name': host_name,
                'Partition Name': partition_name,
                'VS Name': v['virtual_name'].split('/')[-1],
                'VIP': v['vip'] if v['vip'] else '',
                'Port': v['port'] if v['port'] else '',
                'Policy Name': v['asm_profile'] if v['asm_profile'] else '',
                'Security Log Profiles': ', '.join(v['security_log_profiles']) if v['security_log_profiles'] else ''
            })
    
    # 呼叫 write_to_excel 輸出到 Excel，設置分頁名稱為 WAF_Policy_list
    write_to_excel(data, output_file, sheet_name="WAF_Policy_list", columns=['Host Name', 'Partition Name', 'VS Name', 'VIP', 'Port', 'Policy Name', 'Security Log Profiles'])