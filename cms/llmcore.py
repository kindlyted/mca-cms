"""
LLM Core — Unified LLM invocation module.

Supports multiple OpenAI-compatible providers (DeepSeek, Kimi, Qwen, Zhipu, etc.)
Configure API keys in .env file.
"""

import os
import json
import re
from pathlib import Path
from openai import OpenAI

# Provider configuration
PROVIDER_CONFIG = {
    "deepseek": {
        "api_key_env": "API_KEY_DS",
        "base_url_env": "URL_DS",
        "default_model": "deepseek-chat",
        "name": "DeepSeek",
    },
    "kimi": {
        "api_key_env": "API_KEY_KIMI",
        "base_url_env": "URL_KIMI",
        "default_model": "kimi-k2-turbo-preview",
        "name": "Moonshot",
    },
    "qwen": {
        "api_key_env": "API_KEY_QWEN",
        "base_url_env": "URL_QWEN",
        "default_model": "qwen3-vl-flash-2026-01-22",
        "name": "QWEN",
    },
    "dmx": {
        "api_key_env": "API_KEY_DMX",
        "base_url_env": "URL_DMX",
        "default_model": "glm-5-free",
        "name": "DMX"
    },
    "zhipu": {
        "api_key_env": "API_KEY_ZHIPU",
        "base_url_env": "URL_ZHIPU",
        "default_model": "glm-4.6v",
        "name": "Zhipu",
    },
}


def invoke_llm(
    provider: str,
    user_input: str,
    prompt_path: Path = None,
    model: str = None,
    temperature: float = 0.7,
    response_format: dict = None,
    max_retries: int = 2,
) -> str:
    """
    Unified LLM invocation function.

    Args:
        provider: Model provider key (e.g. 'zhipu', 'deepseek')
        user_input: The user message content
        prompt_path: Path to system prompt file (.prompt)
        model: Override default model name
        temperature: Sampling temperature
        response_format: e.g. {'type': 'json_object'}
        max_retries: Number of retries on failure

    Returns:
        The model's response text
    """
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        raise ValueError(f"Unsupported provider: {provider}. Available: {list(PROVIDER_CONFIG.keys())}")

    api_key = os.getenv(config["api_key_env"])
    base_url = os.getenv(config["base_url_env"])
    model_name = model or config["default_model"]

    if not api_key or not base_url:
        raise ValueError(f"Missing env vars: {config['api_key_env']} and {config['base_url_env']}")

    # Load system prompt
    system_prompt = None
    if prompt_path and Path(prompt_path).exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    client = OpenAI(api_key=api_key, base_url=base_url)

    print(f"[{config['name']}] Calling model: {model_name}")
    if system_prompt:
        print(f"  System prompt length: {len(system_prompt)} chars")

    for attempt in range(max_retries + 1):
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_input})

            request_params = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "temperature": temperature,
            }
            if response_format:
                request_params["response_format"] = response_format

            completion = client.chat.completions.create(**request_params)
            answer = completion.choices[0].message.content

            print(f"[{config['name']}] Response received ({len(answer)} chars)")
            return answer

        except Exception as e:
            print(f"[{config['name']}] Attempt {attempt + 1}/{max_retries + 1} failed: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"LLM call failed after {max_retries + 1} attempts: {e}")


def invoke_llm_json(
    provider: str,
    user_input: str,
    prompt_path: Path = None,
    **kwargs,
) -> dict:
    """
    Convenience wrapper: invoke LLM and parse response as JSON.

    Returns:
        Parsed dictionary from LLM response
    """
    response = invoke_llm(
        provider=provider,
        user_input=user_input,
        prompt_path=prompt_path,
        response_format={"type": "json_object"},
        **kwargs,
    )

    def _clean_json(text: str) -> str:
        """Remove invalid control characters except tab/newline/carriage return."""
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    def _try_parse(text: str) -> dict:
        text = _clean_json(text)
        return json.loads(text)

    try:
        return _try_parse(response)
    except json.JSONDecodeError as e:
        # Some providers return markdown-wrapped JSON (```json ... ```) despite response_format
        stripped = response.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r'^```(?:json)?\s*', '', stripped)
            stripped = re.sub(r'\s*```\s*$', '', stripped)
        try:
            return _try_parse(stripped)
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response (first 500 chars): {response[:500]}")
            raise
