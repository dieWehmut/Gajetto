import os
import sys
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import ctypes
import time

# 历史记录文件路径
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'rename_history.json')

def refresh_explorer(path=None):
    """刷新 Windows 资源管理器显示
    
    Args:
        path: 要刷新的文件或文件夹路径(可选)
    """
    try:
        # 获取目录路径
        if path:
            dir_path = os.path.dirname(path) if os.path.isfile(path) else path
        else:
            dir_path = None
        
        # 方法1: 使用 SHChangeNotify API 通知系统
        if dir_path:
            # 更新单个项目
            ctypes.windll.shell32.SHChangeNotify(
                0x0002,  # SHCNE_UPDATEITEM
                0x3005,  # SHCNF_PATHW | SHCNF_FLUSHNOWAIT
                ctypes.c_wchar_p(path), 
                None
            )
            # 更新目录
            ctypes.windll.shell32.SHChangeNotify(
                0x1000,  # SHCNE_UPDATEDIR
                0x3005,  # SHCNF_PATHW | SHCNF_FLUSHNOWAIT
                ctypes.c_wchar_p(dir_path), 
                None
            )
        
        # 方法2: 全局刷新
        ctypes.windll.shell32.SHChangeNotify(
            0x8000000,  # SHCNE_ASSOCCHANGED
            0x3000,     # SHCNF_FLUSHNOWAIT
            None, 
            None
        )
        
        # 方法3: 向所有资源管理器窗口发送 F5 刷新消息
        # 这是最有效的方法,相当于用户按下 F5 键
        HWND_BROADCAST = 0xFFFF
        WM_COMMAND = 0x0111
        ID_FILE_REFRESH = 0xA220  # 资源管理器的刷新命令ID
        
        # 广播刷新消息到所有窗口
        ctypes.windll.user32.PostMessageW(
            HWND_BROADCAST,
            WM_COMMAND,
            ID_FILE_REFRESH,
            0
        )
        
    except Exception as e:
        pass  # 刷新失败也不影响重命名功能


def load_history():
    """加载重命名历史记录
    
    返回格式:
    {
        "文件完整路径": [
            {"old_path": "旧路径1", "old_name": "旧名1", "timestamp": "时间1"},
            {"old_path": "旧路径2", "old_name": "旧名2", "timestamp": "时间2"},
            ...
        ]
    }
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 兼容旧格式:如果是字典而不是列表,转换为列表格式
                converted = {}
                for key, value in data.items():
                    if isinstance(value, dict) and 'old_path' in value:
                        # 旧格式:单个记录,转为列表
                        converted[key] = [value]
                    elif isinstance(value, list):
                        # 新格式:已经是列表
                        converted[key] = value
                    else:
                        converted[key] = [value]
                return converted
        except:
            return {}
    return {}

def save_history(history, merge=True):
    """保存重命名历史记录
    
    Args:
        history: 要保存的历史记录
        merge: 是否与现有记录合并,False则直接覆盖
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        
        if merge:
            # 保存前先读取现有记录,合并后再保存
            existing = {}
            if os.path.exists(HISTORY_FILE):
                try:
                    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                except:
                    pass
            
            # 合并记录
            existing.update(history)
            history = existing
        
        # 保存到文件
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        # 不弹窗,只返回False,让调用者决定如何处理
        return False

def batch_rename(files):
    """批量重命名功能"""
    if not files:
        messagebox.showwarning("警告", "没有选择任何文件")
        return
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
        
        # 每次处理文件前重新加载历史记录
        history = load_history()
        
        # 创建重命名窗口
        root = tk.Tk()
        root.title("重命名文件")
        root.geometry("500x150")
        root.resizable(False, False)
        
        # 居中显示
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        dir_path = os.path.dirname(file_path)
        old_name = os.path.basename(file_path)
        
        # 显示当前文件名
        label_frame = tk.Frame(root, pady=10)
        label_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(label_frame, text="当前文件名:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        tk.Label(label_frame, text=old_name, font=("微软雅黑", 10, "bold"), fg="blue").pack(side=tk.LEFT, padx=10)
        
        # 输入新文件名
        input_frame = tk.Frame(root, pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="新文件名:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        entry = tk.Entry(input_frame, font=("微软雅黑", 10), width=35)
        entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        entry.insert(0, old_name)
        
        # 只选中文件名部分,不包括扩展名
        if '.' in old_name:
            # 找到最后一个点的位置
            last_dot = old_name.rfind('.')
            entry.select_range(0, last_dot)
            entry.icursor(last_dot)  # 光标放在扩展名前
        else:
            # 没有扩展名,选中全部
            entry.select_range(0, tk.END)
        
        entry.focus()
        
        # 重命名结果
        result = {'renamed': False, 'new_name': None}
        
        def do_rename():
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showerror("错误", "文件名不能为空")
                return
            
            if new_name == old_name:
                result['renamed'] = False
                root.destroy()
                return
            
            new_path = os.path.join(dir_path, new_name)
            
            # 检查新文件名是否已存在
            # 注意:需要区分"仅修改大小写"和"真正的文件已存在"
            is_case_only_change = (new_path.lower() == file_path.lower() and new_path != file_path)
            
            if os.path.exists(new_path) and not is_case_only_change:
                if not messagebox.askyesno("确认", f"文件 '{new_name}' 已存在,是否覆盖?"):
                    return
            
            try:
                # 执行重命名
                # Windows 文件系统不区分大小写,仅修改大小写需要两步操作
                is_case_only_change = (new_path.lower() == file_path.lower() and new_path != file_path)
                
                if is_case_only_change:
                    # 第一步:先重命名到临时名称
                    temp_path = file_path + ".tmp_rename"
                    os.rename(file_path, temp_path)
                    # 第二步:再重命名到目标名称
                    os.rename(temp_path, new_path)
                else:
                    # 普通重命名
                    os.rename(file_path, new_path)
                
                # 记录历史并立即保存(使用栈结构,支持多次修改)
                # 检查当前文件是否已有历史记录
                if file_path in history:
                    # 当前文件已有历史,将其历史转移到新路径
                    if new_path not in history:
                        history[new_path] = []
                    history[new_path] = history[file_path].copy()
                    del history[file_path]
                else:
                    # 当前文件没有历史,创建新的
                    if new_path not in history:
                        history[new_path] = []
                
                # 添加本次重命名记录到栈顶
                history[new_path].append({
                    'old_path': file_path,
                    'old_name': old_name,
                    'timestamp': datetime.now().isoformat()
                })
                
                save_history(history)
                
                # 刷新资源管理器显示,特别是对于仅修改大小写的情况
                time.sleep(0.05)  # 短暂延迟确保文件系统完成
                refresh_explorer(new_path)
                
                result['renamed'] = True
                result['new_name'] = new_name
                root.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"重命名失败: {str(e)}")
        
        def skip_rename():
            result['renamed'] = False
            root.destroy()
        
        # 按钮
        button_frame = tk.Frame(root, pady=10)
        button_frame.pack(fill=tk.X, padx=20)
        
        tk.Button(button_frame, text="确定", command=do_rename, width=10, 
                 font=("微软雅黑", 9), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="跳过", command=skip_rename, width=10,
                 font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        entry.bind('<Return>', lambda e: do_rename())
        entry.bind('<Escape>', lambda e: skip_rename())
        
        root.mainloop()

def restore_rename(files):
    """恢复重命名功能"""
    if not files:
        messagebox.showwarning("警告", "没有选择任何文件")
        return
    
    history = load_history()
    restored_list = []  # 成功恢复的文件列表 (新名->旧名)
    failed_files = []   # 失败的文件列表
    
    # 执行恢复,不弹出任何中间提示
    for file_path in files:
        try:
            if file_path in history and len(history[file_path]) > 0:
                # 从栈顶取出最后一次修改记录
                old_info = history[file_path][-1]
                old_path = old_info['old_path']
                old_name = old_info['old_name']
                current_name = os.path.basename(file_path)
                
                # 检查当前文件是否存在
                if not os.path.exists(file_path):
                    failed_files.append(f"{current_name}: 文件不存在")
                    continue
                
                # 检查旧路径是否已存在(且不是当前文件)
                # 注意: Windows 不区分大小写, 需要用小写比较路径
                is_same_file = (old_path.lower() == file_path.lower())
                
                if os.path.exists(old_path) and not is_same_file:
                    # 真的被占用了,自动重命名为 xx(1), xx(2) 等
                    dir_path = os.path.dirname(old_path)
                    base_name = os.path.basename(old_path)
                    
                    # 分离文件名和扩展名
                    if '.' in base_name:
                        name_part = base_name.rsplit('.', 1)[0]
                        ext_part = '.' + base_name.rsplit('.', 1)[1]
                    else:
                        name_part = base_name
                        ext_part = ''
                    
                    # 查找可用的文件名
                    counter = 1
                    while True:
                        new_old_path = os.path.join(dir_path, f"{name_part}({counter}){ext_part}")
                        if not os.path.exists(new_old_path):
                            old_path = new_old_path
                            old_name = os.path.basename(old_path)
                            break
                        counter += 1
                
                # 恢复文件名
                try:
                    os.rename(file_path, old_path)
                    # 刷新资源管理器显示
                    time.sleep(0.05)
                    refresh_explorer(old_path)
                    # 记录成功恢复
                    restored_list.append((current_name, old_name))
                    
                    # 从栈中移除最后一条记录
                    history[file_path].pop()
                    
                    # 如果栈为空,删除整个key
                    if len(history[file_path]) == 0:
                        del history[file_path]
                    # 如果恢复后的路径在历史中,需要更新
                    # 例如: A->B->C, 恢复C->B后, B的历史应该还在
                    
                except Exception as e:
                    failed_files.append(f"{current_name}: {str(e)}")
            else:
                current_name = os.path.basename(file_path)
                failed_files.append(f"{current_name}: 未找到历史记录")
        except Exception as e:
            # 捕获所有异常,避免弹窗
            try:
                current_name = os.path.basename(file_path)
            except:
                current_name = str(file_path)
            failed_files.append(f"{current_name}: {str(e)}")
    
    # 保存更新后的历史记录(直接覆盖,不合并)
    if restored_list:
        try:
            save_history(history, merge=False)
        except:
            pass  # 保存失败也不弹窗,在结果中说明
    
    # 只显示一个结果弹窗
    if restored_list or failed_files:
        msg_parts = []
        
        # 成功恢复的文件
        if restored_list:
            msg_parts.append(f"✓ 成功恢复 {len(restored_list)} 个文件:\n")
            for current, old in restored_list[:10]:  # 最多显示10个
                msg_parts.append(f"  {current} → {old}")
            if len(restored_list) > 10:
                msg_parts.append(f"  ...还有 {len(restored_list) - 10} 个文件")
        
        # 失败的文件
        if failed_files:
            if msg_parts:
                msg_parts.append("\n")
            msg_parts.append(f"✗ 失败 {len(failed_files)} 个文件:\n")
            for fail in failed_files[:10]:  # 最多显示10个
                msg_parts.append(f"  {fail}")
            if len(failed_files) > 10:
                msg_parts.append(f"  ...还有 {len(failed_files) - 10} 个")
        
        msg = "\n".join(msg_parts)
        
        if restored_list and not failed_files:
            messagebox.showinfo("恢复成功", msg)
        elif failed_files and not restored_list:
            messagebox.showerror("恢复失败", msg)
        else:
            messagebox.showwarning("部分恢复成功", msg)
    else:
        messagebox.showinfo("提示", "没有可恢复的文件")

def main():
    if len(sys.argv) < 3:
        messagebox.showerror("错误", "参数不足")
        return
    
    action = sys.argv[1]
    files = sys.argv[2:]
    
    if action == "batch":
        batch_rename(files)
    elif action == "restore":
        restore_rename(files)
    else:
        messagebox.showerror("错误", f"未知操作: {action}")

if __name__ == "__main__":
    main()
