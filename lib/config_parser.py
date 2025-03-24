# lib/config_parser.py
import re
from pathlib import Path

def parse_virtual_ip(config_content):
    """提取 Virtual Server 的 VIP 和 Port"""
    results = {}
    virtual_blocks = re.findall(r'ltm virtual .+? {[\s\S]+?\n}', config_content)
    
    for block in virtual_blocks:
        name_match = re.match(r'ltm virtual\s+([^{]+){', block)
        if not name_match:
            print("無法解析名稱，區塊預覽：", block[:100])
            continue
        virtual_name = name_match.group(1).strip()
        destination_pattern = r'destination\s+\/[^/]+\/(\d+\.\d+\.\d+\.\d+):(\d+)'
        destination_match = re.search(destination_pattern, block)
        
        if destination_match:
            results[virtual_name] = {
                'vip': destination_match.group(1),
                'port': destination_match.group(2)
            }
            print(f"{virtual_name} 找到 VIP: {results[virtual_name]['vip']}, Port: {results[virtual_name]['port']}")
        else:
            results[virtual_name] = {'vip': None, 'port': None}
            print(f"{virtual_name} 未找到 VIP 和 Port")
    
    return results

def parse_asm_profiles(config_content):
    """提取 Virtual Server 的 ASM Profile 與 Security Log Profiles"""
    results = []
    virtual_blocks = re.findall(r'ltm virtual .+? {[\s\S]+?\n}', config_content)
    
    print(f"找到 {len(virtual_blocks)} 個 ltm virtual 區塊")
    for block in virtual_blocks:
        name_match = re.match(r'ltm virtual\s+([^{]+){', block)
        if not name_match:
            print("無法解析名稱，區塊預覽：", block[:100])
            continue
        virtual_name = name_match.group(1).strip()
        print(f"{virtual_name} 內容預覽（前200字元）：{block[:200]}")
        
        result = {
            'virtual_name': virtual_name,
            'asm_partition': None,
            'asm_profile': None,
            'security_log_profiles': []
        }
        
        # 檢查 fastL4
        fastl4_pattern = r'profiles\s*{[\s\S]*?/Common/fastL4\s*{[\s\S]*?}'
        fastl4_match = re.search(fastl4_pattern, block)
        if fastl4_match:
            result['asm_profile'] = "Performance L4"
            print(f"{virtual_name} 找到 fastL4 profile，設為 Performance L4")
        else:
            # 只有在無 fastL4 時檢查 ASM_XXXX
            profiles_asm_pattern = r'profiles\s*{[\s\S]*?(/(\w+)/ASM_[^\s{]+)[\s\S]*?}'
            profiles_asm_match = re.search(profiles_asm_pattern, block)
            if profiles_asm_match:
                asm_full = profiles_asm_match.group(1)
                asm_partition = profiles_asm_match.group(2)
                result['asm_partition'] = f"/{asm_partition}"
                result['asm_profile'] = asm_full.split('/', 2)[-1]
                print(f"{virtual_name} 找到 ASM profile: {result['asm_partition']}/{result['asm_profile']}")
        
        # 提取 Security Log Profiles（僅在有 ASM_XXXX 時）
        security_pattern = r'security-log-profiles\s*{\s*([^}]+)\s*}'
        security_match = re.search(security_pattern, block, re.DOTALL)
        if security_match and result['asm_profile'] and result['asm_profile'] != "Performance L4":
            security_content = security_match.group(1).strip()
            profiles = re.findall(r'(/[^{}\s]+)', security_content)
            result['security_log_profiles'] = [p.split('/')[-1] for p in profiles]
            print(f"{virtual_name} 找到 security-log-profiles: {result['security_log_profiles']}")
        
        results.append(result)
    
    return results

def read_and_parse_bigip_configs(base_path):
    """遍歷目錄，讀取並解析所有 bigip.conf 檔案"""
    all_results = {}
    base_dir = Path(base_path)
    
    if not base_dir.exists():
        print(f"錯誤：基礎路徑 {base_path} 不存在")
        return all_results
        
    print(f"正在掃描目錄：{base_path}")
    for root_dir in base_dir.iterdir():
        if root_dir.is_dir():
            config_path = root_dir / "config" / "partitions"
            if config_path.exists() and config_path.is_dir():
                print(f"找到 partitions 目錄：{config_path}")
                for partition_dir in config_path.iterdir():
                    if partition_dir.is_dir():
                        config_file = partition_dir / "bigip.conf"
                        if config_file.exists():
                            print(f"發現 bigip.conf：{config_file}")
                            try:
                                with open(config_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # 分別解析 VIP 與 ASM
                                    vip_results = parse_virtual_ip(content)
                                    asm_results = parse_asm_profiles(content)
                                    # 合併結果
                                    parsed_results = []
                                    for result in asm_results:
                                        virtual_name = result['virtual_name']
                                        combined_result = {
                                            'virtual_name': virtual_name,
                                            'vip': vip_results.get(virtual_name, {}).get('vip'),
                                            'port': vip_results.get(virtual_name, {}).get('port'),
                                            'asm_partition': result['asm_partition'],
                                            'asm_profile': result['asm_profile'],
                                            'security_log_profiles': result['security_log_profiles']
                                        }
                                        parsed_results.append(combined_result)
                                    if parsed_results:
                                        all_results[str(config_file)] = parsed_results
                                        print(f"成功解析 {len(parsed_results)} 個 virtual server")
                                    else:
                                        print(f"{config_file} 中沒有成功解析任何 ltm virtual 區塊")
                            except Exception as e:
                                print(f"處理檔案 {config_file} 時發生錯誤: {str(e)}")
            else:
                print(f"未找到 config/partitions 目錄於：{root_dir}")
    
    return all_results