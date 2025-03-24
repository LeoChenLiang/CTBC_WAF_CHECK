# main.py
import os
import sys
from datetime import datetime
from lib.file_handler import create_folders_for_ucs_files, extract_bigip_conf_from_ucs_using_tar
from lib.config_parser import read_and_parse_bigip_configs
from lib.excel_writer import export_to_excel

# 設置標準輸出編碼為 UTF-8，避免印出時亂碼
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    ucs_files_dir = r"C:\Users\Euclid Chen\Desktop\所有python\CTBC_WAF_CHECK_V2\file_input"
    output_base_dir = r"C:\Users\Euclid Chen\Desktop\所有python\CTBC_WAF_CHECK_V2\file_output"
    
    # 獲取當前時間
    NOW = datetime.now()
    FORMATTED_NOW = NOW.strftime("%Y%m%d%H%M")
    
    # 如有需要先建立資料夾或解壓 .ucs 檔
    #create_folders_for_ucs_files(ucs_files_dir)
    #extract_bigip_conf_from_ucs_using_tar(ucs_files_dir)
    
    # 解析配置並生成結果
    results = read_and_parse_bigip_configs(ucs_files_dir)
    
    if not results:
        print("沒有找到任何符合條件的資料")
    else:
        for file_path, virtuals in results.items():
            print(f"\n檔案: {file_path}")
            for v in virtuals:
                print(f"Virtual Server: {v['virtual_name']}")
                if v['vip']:
                    print(f"VIP: {v['vip']}, Port: {v['port']}")
                if v['asm_partition']:
                    print(f"ASM Partition: {v['asm_partition']}")
                if v['asm_profile']:
                    print(f"ASM Profile: {v['asm_profile']}")
                if v['security_log_profiles']:
                    print(f"Security Log Profiles: {v['security_log_profiles']}")
                print("-" * 50)
        
        # 輸出到 Excel
        output_file = os.path.join(output_base_dir, f"CTBC_WAF_CHECK_{FORMATTED_NOW}.xlsx")
        export_to_excel(results, output_file)