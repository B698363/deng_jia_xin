# 在Python中快速验证字体文件有效性（需安装fonttools）
from fontTools.ttLib import TTFont

try:
    font = TTFont('d:/code/邓佳鑫/static/font/a.ttf')
    print(f"字体文件有效，包含 {len(font['glyf'].glyphs)} 个字形")
except Exception as e:
    print(f"字体文件损坏：{str(e)}")