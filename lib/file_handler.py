# lib/file_handler.py
import os
import tarfile
import shutil

def create_folders_for_ucs_files(ucs_dir):
    """創建用於儲存 .ucs 檔案解壓後檔案的資料夾"""
    ucs_files = [f for f in os.listdir(ucs_dir) if f.endswith(".ucs")]
    print("找到的 .ucs 檔案：", ucs_files)
    if not ucs_files:
        print("警告：指定目錄中沒有 .ucs 檔案")
    for filename in ucs_files:
        folder = os.path.join(ucs_dir, os.path.splitext(filename)[0])
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("已建立資料夾：", folder)
        else:
            print("資料夾已存在：", folder)

def extract_bigip_conf_from_ucs_using_tar(directory):
    """從 .ucs 檔案中提取特定的 bigip.conf 檔案"""
    ucs_files = [f for f in os.listdir(directory) if f.endswith(".ucs")]
    if not ucs_files:
        print("警告：沒有找到 .ucs 檔案可解壓")
        return
    for filename in ucs_files:
        filepath = os.path.join(directory, filename)
        extraction_path = os.path.join(directory, os.path.splitext(filename)[0])
        print(f"正在解壓 {filename} 到 {extraction_path}")
        try:
            with tarfile.open(filepath, 'r') as tar:
                for member in tar.getmembers():
                    if member.path.startswith("config/partitions/"):
                        target_path = os.path.join(extraction_path, member.path)
                        if member.isdir():
                            os.makedirs(target_path, exist_ok=True)
                        elif member.isfile() and os.path.basename(member.path) == 'bigip.conf':
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with tar.extractfile(member) as src, open(target_path, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                                print(f"已提取: {target_path}")
                    elif member.path in ["config/bigip_base.conf", "config/bigip.conf"]:
                        target_path = os.path.join(extraction_path, os.path.basename(member.path))
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with tar.extractfile(member) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                            print(f"已提取: {target_path}")
            print(f"{filename} 解壓完成")
        except Exception as e:
            print(f"處理 {filename} 時發生錯誤：{e}")