"""
创建图标文件
使用PIL库创建简单的图标
"""
import os

try:
    from PIL import Image, ImageDraw, ImageFont
    
    def create_icon(text, bg_color, filename):
        """创建一个简单的图标"""
        # 创建32x32的图像
        size = 32
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        margin = 2
        draw.ellipse([margin, margin, size-margin, size-margin], 
                     fill=bg_color, outline=(255, 255, 255, 255), width=1)
        
        # 绘制文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("msyh.ttc", 14)
        except:
            font = ImageFont.load_default()
        
        # 计算文字位置(居中)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 保存为ICO格式
        icon_path = os.path.join(os.path.dirname(__file__), filename)
        img.save(icon_path, format='ICO', sizes=[(32, 32)])
        print(f"已创建图标: {filename}")
        return True
    
    # 创建批量重命名图标(蓝色)
    create_icon("改", (33, 150, 243), "batch_rename.ico")
    
    # 创建恢复重命名图标(橙色)
    create_icon("还", (255, 152, 0), "restore_rename.ico")
    
    print("图标创建成功!")

except ImportError:
    print("未安装PIL库,正在安装...")
    import subprocess
    try:
        subprocess.check_call(["pip", "install", "Pillow"])
        print("PIL库安装成功,请重新运行安装程序")
    except:
        print("PIL库安装失败,将创建备用图标...")
        # 创建一个最简单的ICO文件(16x16透明图标)
        def create_simple_ico(filename):
            # ICO文件头和最简单的16x16图标数据
            ico_data = bytes([
                # ICO文件头
                0, 0, 1, 0, 1, 0,  # 文件类型和图标数量
                16, 16, 0, 0, 1, 0, 32, 0,  # 图标目录
                0x40, 1, 0, 0, 22, 0, 0, 0,  # 图标大小和偏移
            ]) + bytes([0] * 16 * 16 * 4)  # 透明像素数据
            
            icon_path = os.path.join(os.path.dirname(__file__), filename)
            with open(icon_path, 'wb') as f:
                f.write(ico_data)
        
        create_simple_ico("batch_rename.ico")
        create_simple_ico("restore_rename.ico")
        print("已创建备用图标")
