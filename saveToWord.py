import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def save_to_word(text_objects, filepath="output.docx"):
    """将带样式的文本保存到Word文档"""
    try:
        if os.path.exists(filepath):
            print(f"文件已存在，且不允许覆盖。")
            return
        # 1. 自动创建目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = Document()
        
        for item in text_objects:
            text = item['text'].strip()
            if not text:  # 跳过空内容
                continue
                
            style = item['attrs'].get('style', '')
            p = doc.add_paragraph()
            
            # 处理对齐方式
            if 'text-align:center' in style:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 处理字体样式
            run = p.add_run(text)
            font = run.font
            font.name = '仿宋_GB2312' if '仿宋' in style else '楷体_GB2312' if '楷体' in style else '方正小标宋简体' if '小标宋' in style else '宋体'
            font.size = Pt(21) if 'font-size:21px' in style else Pt(29) if 'font-size:29px' in style else Pt(12)
            
            # 处理颜色
            if 'color:rgb(255,0,0)' in style:
                font.color.rgb = RGBColor(255, 0, 0)  # 红色
            elif 'color:rgb(0,112,192)' in style:
                font.color.rgb = RGBColor(0, 112, 192)  # 蓝色
                
            # 处理行距 (简化处理)
            if 'line-height:43px' in style:
                p.paragraph_format.line_spacing = Pt(43)
            elif 'line-height:37px' in style:
                p.paragraph_format.line_spacing = Pt(37)
                
            # 首行缩进
            if 'text-indent:43px' in style:
                p.paragraph_format.first_line_indent = Pt(43)
        
        doc.save(filepath)
        print(f"Word文档已生成: {filepath}")
        return True
    
    except Exception as e:
        print(f"文件保存失败: {str(e)}")
        return False

# 使用示例
# text_objects = [...]  # 你的数据
# save_to_word(text_objects,text_objects[1].text + ".docx" )