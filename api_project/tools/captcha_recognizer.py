import base64
import io
import os
from pathlib import Path

from PIL import Image
import pytesseract

# Windows 系统下 Tesseract-OCR 的默认安装路径
# 如果实际安装路径不同，请修改此配置或在使用前动态设置
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _validate_kimi_api_key(api_key: str) -> None:
    """
    校验 Kimi API Key 是否合法。

    :param api_key: 待校验的 API Key。
    :raises ValueError: Key 为空或包含非 ASCII 字符时抛出。
    """
    if not api_key or not api_key.strip():
        raise ValueError("Kimi API Key 不能为空，请检查是否已正确设置。")

    # HTTP 协议要求请求头必须是 ASCII 编码，若 Key 包含中文会触发 UnicodeEncodeError
    try:
        api_key.encode("ascii")
    except UnicodeEncodeError as e:
        raise ValueError(
            f"Kimi API Key 包含非 ASCII 字符（如中文），无法用于 HTTP 请求头。\n"
            f"当前 Key 前 20 个字符: {api_key[:20]!r}，错误位置: {e.start}-{e.end}"
        ) from e


def _encode_image_to_data_url(image_path: str) -> str:
    """
    读取本地图片文件并转为 Base64 Data URL 格式。

    :param image_path: 图片本地路径。
    :return: 形如 data:image/png;base64,... 的字符串。
    """
    image_path = Path(image_path).resolve()
    # 根据文件扩展名确定图片格式，不识别时默认按 png 处理
    ext = image_path.suffix.lstrip(".").lower()
    if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
        ext = "png"

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/{ext};base64,{image_base64}"


def recognize_captcha_tesseract(
    image_bytes: bytes,
    whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    threshold: int = 128,
    scale: int = 2,
    psm: int = 7
) -> str:
    """
    使用 Tesseract OCR 从验证码图片中识别文字。

    :param image_bytes: 接口返回的图片二进制数据。
    :param whitelist: 允许识别的字符白名单。
    :param threshold: 二值化阈值，0-255。
    :param scale: 放大倍数，小图建议放大以提升识别率。
    :param psm: Tesseract 页面分割模式，验证码一般用 7。
    :return: 识别后的验证码字符串。
    """
    image = Image.open(io.BytesIO(image_bytes))

    # 灰度化、二值化、放大
    gray_image = image.convert("L")
    binary_image = gray_image.point(lambda x: 0 if x < threshold else 255, "1")

    if scale > 1:
        new_size = (image.width * scale, image.height * scale)
        binary_image = binary_image.resize(new_size, Image.Resampling.LANCZOS)

    config = f"--psm {psm}"
    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"

    code = pytesseract.image_to_string(binary_image, config=config)
    return code.strip().replace(" ", "").replace("\n", "")


def recognize_captcha_ddddocr(image_bytes: bytes) -> str:
    """
    使用 ddddocr 从验证码图片中识别文字。

    ddddocr 是基于 ONNX 的本地 OCR 库，对普通英文/数字验证码效果较好，
    无需额外安装 Tesseract 引擎。

    :param image_bytes: 接口返回的图片二进制数据。
    :return: 识别后的验证码字符串。
    """
    import ddddocr

    ocr = ddddocr.DdddOcr(show_ad=False)
    return ocr.classification(image_bytes)


def recognize_captcha_by_kimi(
    image_path: str,
    api_key: str,
    model: str = "kimi-k2.6",
    base_url: str = "https://api.moonshot.cn/v1",
    debug: bool = False
) -> str:
    """
    使用 Kimi 视觉大模型识别本地图片验证码。

    该方法使用 requests 直接调用 Kimi API，便于排查网络、鉴权、模型等问题。

    :param image_path: 验证码图片的本地路径。
    :param api_key: Kimi 开放平台申请的 API Key。
    :param model: 使用的模型名称，默认 kimi-k2.6；如无效可尝试 kimi-latest。
    :param base_url: Kimi API 的基础地址，默认国内地址 https://api.moonshot.cn/v1，
                    海外用户可改用 https://api.moonshot.ai/v1。
    :param debug: 是否打印完整响应内容，便于排查识别为空的问题。
    :return: 识别后的验证码字符串。
    :raises: 请求失败时抛出异常，并在异常信息中附带 HTTP 状态码和响应内容。
    """
    import requests
    from PIL import Image

    _validate_kimi_api_key(api_key)

    # 对验证码图片适当放大，提升大模型对细小字符的识别率
    original = Image.open(image_path)
    scaled = original.resize((original.width * 3, original.height * 3), Image.Resampling.LANCZOS)

    import io as _io
    buffer = _io.BytesIO()
    scaled.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    image_url = f"data:image/png;base64,{image_base64}"

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": (
                            "这是一张验证码图片，图片中可能包含干扰线。"
                            "请仔细识别图片中的每一个字符（字母和/或数字），"
                            "按从左到右的顺序输出，只输出识别到的字符，"
                            "不要加任何解释、标点或空格。"
                        )
                    }
                ]
            }
        ],
        "max_tokens": 200,
        "thinking": {"type": "disabled"}
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    # 如果响应状态码不是 200，抛出包含详细信息的异常，方便排查
    if response.status_code != 200:
        raise RuntimeError(
            f"Kimi API 请求失败，状态码: {response.status_code}, "
            f"响应内容: {response.text}, 请求地址: {url}, 模型: {model}"
        )

    result = response.json()
    if debug:
        print(f"[debug] 完整响应: {result}")

    message = result["choices"][0]["message"]
    content = message.get("content", "").strip()

    # 如果 content 为空但存在 reasoning_content，则尝试从 reasoning_content 中提取
    if not content and "reasoning_content" in message:
        reasoning = message["reasoning_content"].strip()
        # 简单提取：找最后出现的引号或等号后的内容
        import re
        # 尝试匹配 "答案是 xxxx"、"验证码是 xxxx"、"输出: xxxx" 等模式
        matches = re.findall(r"[是:：]\s*['\"]?([a-zA-Z0-9]+)['\"]?", reasoning)
        if matches:
            content = matches[-1]

    return content


def test_kimi_connection(api_key: str, base_url: str = "https://api.moonshot.cn/v1") -> None:
    """
    测试 Kimi API Key 和 base_url 是否能正常连通（不消耗图片识别 token）。

    :param api_key: Kimi API Key。
    :param base_url: Kimi API 基础地址。
    """
    import requests

    _validate_kimi_api_key(api_key)
    url = f"{base_url.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, timeout=30)

    print(f"请求地址: {url}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")


def recognize_captcha(image_bytes: bytes, engine: str = "ddddocr", **kwargs) -> str:
    """
    通用验证码识别入口（支持本地引擎）。

    :param image_bytes: 接口返回的图片二进制数据。
    :param engine: 识别引擎，可选 "ddddocr" 或 "tesseract"。
    :param kwargs: 传递给具体识别引擎的参数。
    :return: 识别后的验证码字符串。
    """
    if engine == "ddddocr":
        return recognize_captcha_ddddocr(image_bytes)
    elif engine == "tesseract":
        return recognize_captcha_tesseract(image_bytes, **kwargs)
    else:
        raise ValueError(f"不支持的验证码识别引擎: {engine}，仅支持 ddddocr、tesseract")
