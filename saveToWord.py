import os
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING

def save_to_word(text_objects, filepath="output.docx"):
    """将带样式的文本保存到Word文档"""
    try:
        if os.path.exists(filepath):
            print(f"文件已存在，且不允许覆盖。")
            return False
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        doc = Document()
        
        # 设置默认节格式（如页边距）
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        
        for item in text_objects:
            text = item['text'].strip()
            if not text:
                continue
                
            style = item['attrs'].get('style', '')
            p = doc.add_paragraph(style='Normal')

            # --- 对齐方式 ---
            if 'text-align: center' in style:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing = Pt(43)  # 行距需要单独设置
            elif 'text-align:right' in style:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
            # --- 字体样式 ---
            run = p.add_run(text)
            font = run.font
            
            # 字体匹配（使用正则更精准）
            font_mapping = {
                r'仿宋|FangSong': '仿宋_GB2312',
                r'楷体|KaiTi': '楷体_GB2312',
                r'小标宋|SimSun': '方正小标宋简体',
                r'黑体|SimHei': '黑体'
            }
            
            for pattern, font_name in font_mapping.items():
                if re.search(pattern, style, re.IGNORECASE):
                    font.name = font_name
                    break
            else:
                font.name = '宋体'
                
            # --- 字号 ---
            size_match = re.search(r'font-size:(\d+)px', style)
            if size_match:
                font.size = Pt(int(size_match.group(1)))
            else:
                font.size = Pt(12)  # 默认字号
                
            # --- 颜色 ---
            color_matches = re.findall(r'rgb$(\d+),\s*(\d+),\s*(\d+)$', style)
            if color_matches:
                r, g, b = map(int, color_matches[0])
                font.color.rgb = RGBColor(r, g, b)
                
            # --- 段落格式 ---
            para_format = p.paragraph_format
            
            # 行距（精确到磅）
            line_match = re.search(r'line-height\s*:\s*(\d+)\s*px', style, re.IGNORECASE)
            if line_match:
                para_format.line_spacing = Pt(float(line_match.group(1)))
                para_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
                
            # 缩进（首行缩进和左右缩进）
            indent_match = re.search(r'text-indent\s*:\s*(\d+)\s*px', style, re.IGNORECASE)
            if indent_match:
                para_format.first_line_indent = Pt(float(indent_match.group(1)))
                
            # 段前段后距
            margin_top = re.search(r'margin-top\s*:\s*(\d+)\s*px', style, re.IGNORECASE)
            margin_bottom = re.search(r'margin-bottom\s*:\s*(\d+)\s*px', style, re.IGNORECASE)
            if margin_top:
                para_format.space_before = Pt(float(margin_top.group(1)))
            if margin_bottom:
                para_format.space_after = Pt(float(margin_bottom.group(1)))
                
            # 文字环绕（简化处理）
            if 'text-wrap-mode: wrap' in style:
                para_format.widow_control = True

        doc.save(filepath)
        print(f"Word文档已生成: {filepath}")
        return True
        
    except Exception as e:
        print(f"文件保存失败: {str(e)}")
        return False

# 使用示例
# text_objects = [...]  # 你的数据
# save_to_word(text_objects,text_objects[1].text + ".docx" )