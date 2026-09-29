"""
AI Image Generator - 文生图模块

使用通义千问（默认）或豆包 Seedream 生成高质量图片，替代 Unsplash 下载。
"""

import os
import io
import requests
from pathlib import Path
from typing import Optional
from PIL import Image

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")

# 导入 AI 服务
try:
    from volcenginesdkarkruntime import Ark
    from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions
    ARK_AVAILABLE = True
except ImportError:
    ARK_AVAILABLE = False

try:
    import dashscope
    from dashscope import MultiModalConversation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


# =============================================================================
# 风格控制提示词模板
# =============================================================================
# style 参数传入后，生图时正面提示词 = 风格控制提示词 + 内容提示词（大模型生成）
# 可选风格:
#   photorealistic  — 真实摄影风（默认），适合 blog/service/provider 通用配图
#   cartoon         — 卡通可爱科普风，适合 service/provider 科普插图
#   ink-wash        — 中国国画水墨风，适合 blog 中医小妙招配图
#   minimalist      — 简约现代风，适合 service 现代医疗配图
#   nature-healing  — 自然疗愈风，适合 wellness/spa 类内容

STYLE_PROMPTS = {
    "photorealistic": {
        "positive": (
            "Professional photography, realistic and natural, cinematic quality, "
            "clean and bright medical environment, authentic lighting, "
            "natural skin tones, genuine expressions, realistic textures, "
            "high resolution, 8K quality, photorealistic rendering"
        ),
        "negative": (
            "cartoon, illustration, drawing, painting, anime, flat design, "
            "vector art, 3D render, CGI looking, artificial, stylized, "
            "ink wash painting, traditional Chinese painting"
        ),
    },
    "cartoon": {
        "positive": (
            "Cute and friendly cartoon illustration style, bright and vibrant colors, "
            "simple clean lines, flat vector design, playful and educational, "
            "appealing to general audience, warm and welcoming atmosphere, "
            "whimsical yet informative, adorable characters, smiling faces, "
            "colorful and engaging, popular science illustration style"
        ),
        "negative": (
            "photorealistic, realistic, photograph, dark lighting, grim, "
            "scary, gory, blood, complex details, oversaturated, "
            "distorted, deformed, ugly characters, horror, rough, messy"
        ),
    },
    "ink-wash": {
        "positive": (
            "Traditional Chinese ink wash painting style (国画水墨风), "
            "elegant brush stroke textures, monochrome with subtle color accents, "
            "artistic and poetic composition, traditional Chinese art aesthetic, "
            "minimalist yet expressive, cultural heritage, "
            "soft flowing lines, ink diffusion effects, rice paper texture, "
            "oriental elegance, zen atmosphere"
        ),
        "negative": (
            "photorealistic, photograph, 3D render, cartoon, flat vector, "
            "bright neon colors, western art style, digital looking, "
            "overly detailed, cluttered composition, modern style"
        ),
    },
    "minimalist": {
        "positive": (
            "Clean minimalist design, soft pastel colors, ample white space, "
            "modern and elegant, simple geometric shapes, gentle gradients, "
            "sophisticated and professional, uncluttered composition, "
            "focused on essential elements, smooth surfaces, "
            "calm and soothing visual style"
        ),
        "negative": (
            "busy background, cluttered, chaotic, overly detailed, "
            "dark and moody, vintage, retro, grunge, heavily textured, "
            "photorealistic, cartoon, ink wash"
        ),
    },
    "nature-healing": {
        "positive": (
            "Nature-inspired healing aesthetic, soft organic shapes, "
            "botanical elements, soothing natural colors, gentle sunlight, "
            "leaves and plants integration, calm and peaceful atmosphere, "
            "holistic wellness vibe, connection to nature, "
            "warm earth tones mixed with soft greens, "
            "serene and restorative ambiance"
        ),
        "negative": (
            "cold clinical setting, dark, gloomy, urban background, "
            "industrial look, harsh lighting, sterile appearance, "
            "cartoon, ink wash, overly artistic"
        ),
    },
}

DEFAULT_STYLE = "photorealistic"

# =============================================================================
# 提示词生成
# =============================================================================

def get_image_prompt(query: str, content_type: str = "blog", style: str = DEFAULT_STYLE) -> str:
    """
    生成正面提示词：风格控制 + 内容描述

    Args:
        query: 原始查询关键词
        content_type: 内容类型 (blog, service, provider)
        style: 图片风格 (见 STYLE_PROMPTS 定义)

    Returns:
        正面提示词
    """
    style_key = style if style in STYLE_PROMPTS else DEFAULT_STYLE
    style_prompt = STYLE_PROMPTS[style_key]["positive"]

    if content_type == "blog":
        content = f"Subject: {query}"
    elif content_type == "service":
        content = f"Subject: {query}, professional service, delivery, client care"
    elif content_type == "provider":
        content = f"Subject: {query}, institution, professional facility"
    elif content_type == "product":
        content = f"Subject: {query}, product, commercial product, product photography"
    else:
        content = f"Subject: {query}"

    return f"{style_prompt}\n\n{content}"


def get_negative_prompt(style: str = DEFAULT_STYLE) -> str:
    """
    生成负面提示词

    Args:
        style: 图片风格

    Returns:
        负面提示词
    """
    style_key = style if style in STYLE_PROMPTS else DEFAULT_STYLE
    base = (
        "low resolution, low quality, distorted limbs, deformed fingers, "
        "oversaturated, wax-like appearance, faceless, overly smooth, "
        "disorganized composition, blurry text, watermark, logo, text overlay"
    )
    style_neg = STYLE_PROMPTS[style_key]["negative"]
    return f"{style_neg}, {base}"


# =============================================================================
# AI 图片生成器
# =============================================================================

class AIGenerator:
    """AI 图片生成器基类"""

    def __init__(self):
        self.api_key_ark = os.getenv("API_KEY_ARK")
        self.url_ark = os.getenv("URL_ARK", "https://ark.cn-beijing.volces.com/api/v3")
        self.api_key_dashscope = os.getenv("API_KEY_DASHSCOPE")
        self.url_dashscope = os.getenv("URL_DASHSCOPE", "https://dashscope.aliyuncs.com/api/v1")

    def generate_seedream(
        self,
        prompt: str,
        model: str = "doubao-seedream-5-0-260128",
        size: str = "2848x1600"
    ) -> Optional[str]:
        """
        使用豆包 Seedream 生成图片

        Args:
            prompt: 提示词
            model: 模型名称
            size: 图片尺寸，格式 "widthxheight" 或预设 "1K", "2K", "4K"

        Returns:
            图片 URL，失败返回 None
        """
        if not ARK_AVAILABLE:
            print("  [AI] volcengine-python-sdk 未安装")
            return None

        if not self.api_key_ark:
            print("  [AI] API_KEY_ARK 未设置")
            return None

        try:
            client = Ark(
                base_url=self.url_ark,
                api_key=self.api_key_ark
            )

            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                sequential_image_generation="disabled",
                response_format="url",
                stream=False,
                watermark=False
            )

            if response.data and len(response.data) > 0:
                return response.data[0].url
            return None

        except Exception as e:
            error_str = str(e)
            print(f"  [AI] Seedream 生成失败: {error_str}")
            return None

    def generate_qwen(
        self,
        prompt: str,
        model: str = "qwen-image-2.0-pro",
        size: str = "1920x1080",
        negative_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        使用通义千问生成图片

        Args:
            prompt: 提示词
            model: 模型名称
            size: 图片尺寸（像素）
            negative_prompt: 负面提示词

        Returns:
            图片 URL，失败返回 None
        """
        if not DASHSCOPE_AVAILABLE:
            print("  [AI] dashscope 未安装")
            return None

        if not self.api_key_dashscope:
            print("  [AI] API_KEY_DASHSCOPE 未设置")
            return None

        try:
            dashscope.base_http_api_url = self.url_dashscope

            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]

            # 解析尺寸
            try:
                width, height = map(int, size.split('x'))
            except ValueError:
                width, height = 1920, 1080

            response = MultiModalConversation.call(
                api_key=self.api_key_dashscope,
                model=model,
                messages=messages,
                result_format='message',
                stream=False,
                watermark=False,
                prompt_extend=True,
                negative_prompt=negative_prompt or "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。",
                size=f"{width}*{height}"
            )

            print(f"  [AI] Qwen 响应状态: {response.status_code}")
            print(f"  [AI] Qwen 响应内容: {response}")

            if response.status_code == 200:
                # 尝试多种方式提取图片 URL
                # 方式1: response.output.choices[0].message.content[0].image_url
                if hasattr(response, 'output') and hasattr(response.output, 'choices'):
                    choices = response.output.choices
                    if choices and len(choices) > 0:
                        first_choice = choices[0]
                        if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
                            content_list = first_choice.message.content
                            print(f"  [AI] Content list: {content_list}")
                            if isinstance(content_list, list) and len(content_list) > 0:
                                first_content = content_list[0]
                                print(f"  [AI] First content: {first_content}")
                                print(f"  [AI] Content type: {type(first_content)}")

                                # 检查是否有 image_url 属性
                                if hasattr(first_content, 'image_url'):
                                    img_url = first_content.image_url
                                    print(f"  [AI] 图片 URL: {img_url}")
                                    return img_url

                                # 检查是否是 dict 且有 image_url 键
                                if isinstance(first_content, dict) and 'image_url' in first_content:
                                    img_url = first_content['image_url']
                                    print(f"  [AI] 图片 URL (dict): {img_url}")
                                    return img_url

                                # 检查是否是 dict 且有 image 键（Qwen 新版返回格式）
                                if isinstance(first_content, dict) and 'image' in first_content:
                                    img_url = first_content['image']
                                    print(f"  [AI] 图片 URL (image key): {img_url}")
                                    return img_url

            print(f"  [AI] 无法从响应中提取图片 URL")
            return None

        except Exception as e:
            print(f"  [AI] Qwen 生成失败: {str(e)}")
            return None


# =============================================================================
# 主要导出函数
# =============================================================================

def generate_image_from_text(
    prompt: str,
    save_path: Path,
    model: str = "qwen-image-2.0-pro",
    size: str = "1920x1080",
    provider: str = "qwen",  # "seedream" or "qwen"
    negative: Optional[str] = None,
) -> Optional[str]:
    """
    使用 AI 生成图片并保存到本地

    Args:
        prompt: 正面提示词
        save_path: 保存路径
        model: 模型名称
        size: 图片尺寸
        provider: 提供商 (seedream 或 qwen)
        negative: 负面提示词

    Returns:
        保存的文件路径，失败返回 None
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    generator = AIGenerator()

    # 生成图片
    if provider == "qwen":
        image_url = generator.generate_qwen(prompt, model=model, size=size, negative_prompt=negative)
    else:
        combined = prompt
        if negative:
            combined = f"{prompt}\n\nNegative prompt: {negative}"
        image_url = generator.generate_seedream(combined, model=model, size=size)

    if not image_url:
        return None

    # 下载图片
    try:
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()

        # 加载图片
        img = Image.open(io.BytesIO(response.content))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # 保存为 WebP
        save_path = save_path.with_suffix('.webp')
        img.save(save_path, format="WEBP", quality=85, method=6)

        size_kb = os.path.getsize(save_path) / 1024
        print(f"  [AI] 生成成功: {save_path.name} ({size_kb:.1f}KB)")
        return str(save_path)

    except Exception as e:
        print(f"  [AI] 保存图片失败: {e}")
        return None


def generate_blog_image(
    query: str,
    save_path: Path,
    aspect_ratio: str = "landscape",
    provider: str = "qwen",
    model: str = "qwen-image-2.0-pro",
    style: str = DEFAULT_STYLE,
) -> Optional[str]:
    """
    为 blog 生成图片

    Args:
        query: 查询关键词
        save_path: 保存路径
        aspect_ratio: "landscape" 或 "portrait"
        provider: 提供商
        model: 模型名称
        style: 图片风格 (见 STYLE_PROMPTS)

    Returns:
        保存的文件路径，失败返回 None
    """
    prompt = get_image_prompt(query, content_type="blog", style=style)
    negative = get_negative_prompt(style)

    if provider == "seedream":
        size = "2848x1600" if aspect_ratio == "landscape" else "1600x2848"
    else:
        size = "1920x1080" if aspect_ratio == "landscape" else "1080x1920"

    return generate_image_from_text(prompt, save_path, model=model, size=size, provider=provider, negative=negative)


def generate_service_image(
    query: str,
    save_path: Path,
    provider: str = "qwen",
    model: str = "qwen-image-2.0-pro",
    style: str = DEFAULT_STYLE,
) -> Optional[str]:
    """
    为 service 生成封面图

    Args:
        query: 查询关键词
        save_path: 保存路径
        provider: 提供商
        model: 模型名称
        style: 图片风格 (见 STYLE_PROMPTS)

    Returns:
        保存的文件路径，失败返回 None
    """
    prompt = get_image_prompt(query, content_type="service", style=style)
    negative = get_negative_prompt(style)
    size = "2848x1600" if provider == "seedream" else "1920x1080"
    return generate_image_from_text(prompt, save_path, model=model, size=size, provider=provider, negative=negative)


def generate_provider_image(
    query: str,
    save_path: Path,
    provider: str = "qwen",
    model: str = "qwen-image-2.0-pro",
    style: str = DEFAULT_STYLE,
) -> Optional[str]:
    """
    为 provider 生成封面图

    Args:
        query: 查询关键词
        save_path: 保存路径
        provider: 提供商
        model: 模型名称
        style: 图片风格 (见 STYLE_PROMPTS)

    Returns:
        保存的文件路径，失败返回 None
    """
    prompt = get_image_prompt(query, content_type="provider", style=style)
    negative = get_negative_prompt(style)
    size = "2848x1600" if provider == "seedream" else "1920x1080"
    return generate_image_from_text(prompt, save_path, model=model, size=size, provider=provider, negative=negative)


def generate_product_image(
    query: str,
    save_path: Path,
    provider: str = "qwen",
    model: str = "qwen-image-2.0-pro",
    style: str = DEFAULT_STYLE,
) -> Optional[str]:
    """
    为 product 生成封面图

    Args:
        query: 查询关键词
        save_path: 保存路径
        provider: 提供商
        model: 模型名称
        style: 图片风格 (见 STYLE_PROMPTS)

    Returns:
        保存的文件路径，失败返回 None
    """
    prompt = get_image_prompt(query, content_type="product", style=style)
    negative = get_negative_prompt(style)
    size = "2848x1600" if provider == "seedream" else "1920x1080"
    return generate_image_from_text(prompt, save_path, model=model, size=size, provider=provider, negative=negative)
