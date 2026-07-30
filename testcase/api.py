import os
import sys
from pathlib import Path

# 将项目根目录加入模块搜索路径，确保无论从哪里运行脚本都能导入 api_project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_project.tools.captcha_recognizer import recognize_captcha_by_kimi, test_kimi_connection

# 验证码图片路径
image_path = r"E:\zdh_project\testcase\vcode.png"

# Kimi API Key，优先从环境变量读取，避免硬编码泄露
api_key = os.environ.get("KIMI_API_KEY")
if not api_key:
    # 如果环境变量未设置，可临时在这里填写（仅本地调试，用完即删）
    api_key = "sk-LH0oiYrZYynIRMhX9ClJuQXgin6RaMs7G54tgapmp8MoKcjH"

# 校验 API Key 是否已配置
if not api_key or not api_key.strip():
    raise ValueError(
        "Kimi API Key 未设置。请在运行前设置环境变量 KIMI_API_KEY，\n"
        "例如 PowerShell 中执行：$env:KIMI_API_KEY='sk-你的Key'"
    )

# 国内官方 API 地址
base_url = "https://api.moonshot.cn/v1"
# 模型名称，根据你的账号实际可用模型填写
# 常见可选：kimi-k2.6、kimi-k2.5-preview、kimi-latest
model = "kimi-k3"

# 先测试 API Key 和 base_url 是否能连通
print("正在测试 Kimi API 连通性...")
test_kimi_connection(api_key, base_url=base_url)

# 调用 Kimi 视觉模型识别验证码
print("\n正在识别验证码...")
code = recognize_captcha_by_kimi(
    image_path,
    api_key=api_key,
    model=model,
    base_url=base_url,
    debug=True  # 调试时打印完整响应，确认后可选关闭
)
print(f"识别到的验证码: {code}")
