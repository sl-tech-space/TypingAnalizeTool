import os

# パス設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 難易度と言語の設定
DIFFICULTY_NAMES = {1: "イージー", 2: "ノーマル", 3: "ハード"}
LANGUAGE_NAMES = {1: "日本語", 2: "英語"}
