import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))