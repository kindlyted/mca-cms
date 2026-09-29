# MCA-CMS 内容生成器

这是 **mca-cms 模板自带的内容管理系统**。它是一个 Python CLI，**让你用自己的 LLM API**（DeepSeek / 智谱 / Kimi / 通义等 OpenAI 兼容接口）自动生成四种实体（`product` / `service` / `partner` / `blog`）的 JSON 内容，直接落盘到站点的 `data/` 目录，站点随即就能渲染这些页面。

- 文本生成走**你自己的 LLM API**（不在代码里绑定任何厂商）。
- 图片下载/生成、远程同步为可选项。
- 核心思路：**改几个文件（配置 / 模板 / 生成器 / 提示词）就能适配你自己的实体与字段**，详见 [二次开发](#二次开发)。

## 快速开始

所有命令在**站点根目录**执行（`cms\main.py` 的相对路径基于站点根），用站点根的 venv Python 运行，**无需 activate**：

```powershell
# 1. 首次装依赖（venv 已由 setup.ps1 创建；若没有，先在站点根跑 .\setup.ps1）
.\venv\Scripts\python.exe -m pip install -r cms\requirements.txt

# 2. 配置 cms/.env（生成站点时已自动创建，只需填 LLM key）
Copy-Item cms\.env.example cms\.env   # 仅当 cms/.env 不存在时需要
```

`.env` 至少配置一个 LLM 提供商（OpenAI 兼容协议）：

```env
# DeepSeek
API_KEY_DS=sk-xxx
URL_DS=https://api.deepseek.com/v1
```

支持的提供商见 `cms/llmcore.py` 的 `PROVIDER_CONFIG`（deepseek / zhipu / kimi / qwen / dmx）。也可用 `--provider` 在命令行切换。

### 生成内容

```powershell
# 商品（落盘 data/products/{category}/{lang}/{slug}.json）
.\venv\Scripts\python.exe cms\main.py product  --name "large exercise mat" -l en

# 服务（data/services/{lang}/{slug}.json）
.\venv\Scripts\python.exe cms\main.py service  --name "acupuncture" -l en

# 伙伴/机构（data/partners/{lang}/{slug}.json；provider 内部名输出为 _type: partner）
.\venv\Scripts\python.exe cms\main.py provider --name "Beijing Tongren Eye Hospital" -l en

# 博客（data/blogs/{lang}/{slug}.json）
.\venv\Scripts\python.exe cms\main.py blog --topic "dental implants cost in Shanghai" -l en

# 所有语言（settings.LANGUAGES 里的语言）
.\venv\Scripts\python.exe cms\main.py blog --topic "..." -l all

# 校验已生成/手写的 JSON
.\venv\Scripts\python.exe cms\main.py validate --files data/blogs/en/some.json
```

> 生成前需先有 `npx prisma generate` 和正常能跑 `npm run build` 的站点环境（本 CMS 只写 `data/`，不参与构建）。

---

## 架构

```
cms/
├── main.py                     # CLI 入口（blog/service/provider/product/validate）
├── llmcore.py                  # 统一 LLM 调用（OpenAI 兼容，多提供商）
├── config/settings.py          # 站点配置：数据目录 / 语言 / 路径 / 图片 / 同步
├── generators/
│   ├── base.py                 # 模板 schema（TEMPLATES）+ 自动填充 + 封面 + 保存
│   ├── blog_generator.py
│   ├── service_generator.py
│   ├── provider_generator.py
│   └── product_generator.py
├── prompts/                    # 给 LLM 的 system prompt（决定它输出哪些字段）
└── validators/                 # JSON schema 校验
```

**生成链路**：`main.py` → 生成器调用 `llmcore`（带 `prompts/*.prompt` 让 LLM 输出字段 JSON）→ 生成器 `_assemble()` 按 `base.py` 的模板组装 → `auto_fill_meta()` 补 id/时间/hreflang/author → `save()` 落盘 `data/`。

---

## 二次开发

这是最重要的一节：**如何把 CMS 定制成你想要的实体与字段**。它不要求你理解整个代码，只需按下面几处改。

### 1. 站点级配置 —— `config/settings.py`

改这一处即可调整全局：

| 字段 | 作用 |
|------|------|
| `LANGUAGES` | 站点支持的语言（默认 `["en","fr","de"]`） |
| `DEFAULT_LANGUAGE` | 默认语言 |
| `BASE_URL` | 生成 canonical / hreflang 用的站点域名 |
| `BLOG_OUTPUT_DIR` / `SERVICE_OUTPUT_DIR` / `PROVIDER_OUTPUT_DIR` / `PRODUCT_OUTPUT_BASE` | 各实体落盘目录 |
| `BLOG_ASSETS_DIR` / … | 各实体图片目录 |
| `DEFAULT_PROVIDER` | 默认 LLM 提供商 |

### 2. 实体字段模板 —— `generators/base.py`

每个实体在 `base.py` 顶部有一个硬编码模板（`BLOG_TEMPLATE` / `SERVICE_TEMPLATE` / `PROVIDER_TEMPLATE` / `PRODUCT_TEMPLATE`），它是该实体的**字段 schema（source of truth）**。改字段 = 改模板。

例如给 `product` 加一个 `"warranty"` 字段：

```python
PRODUCT_TEMPLATE = {
    ...
    "inStock": True,
    "warranty": "",          # ← 新增字段
    ...
}
```

> 注意：模板里的键会作为**必填项**被 `validate_against_template()` 检查；运行时不强制，但缺了会打 warning。

### 3. 生成逻辑 —— `generators/{entity}_generator.py`

- `_assemble()`：把 LLM 输出的 `content_data` 逐字段填进模板。**新增/改名某个字段就在这里映射**。
- `generate()`：控制生成流程（如 service 是先写 markdown 再翻译）。

### 4. 提示词 —— `prompts/{entity}_content.prompt`

决定 LLM 输出哪些字段。**当你改了模板，一定要同步改 prompt 的 JSON 输出结构**，否则 LLM 不会输出新字段。例如加了 `warranty`：

```
{
  ...
  "inStock": true,
  "warranty": "10-year manufacturer warranty",
  ...
}
```

### 5. 新增一个全新实体（完整步骤）

假设你要加一个 `testimonial`（客户案例）实体：

1. **`config/settings.py`**：加输出/资产目录
   ```python
   TESTIMONIAL_OUTPUT_DIR = DATA_DIR / "testimonials"
   TESTIMONIAL_ASSETS_DIR = DATA_DIR / "assets" / "testimonials"
   ```
2. **`generators/base.py`**：定义 `TESTIMONIAL_TEMPLATE` 并加入 `TEMPLATES`。
3. **`generators/testimonial_generator.py`**：新建，继承 `BaseGenerator`，`CONTENT_TYPE = "testimonial"`，实现 `generate()` 与 `_assemble()`。
4. **`prompts/testimonial_content.prompt`**：告诉 LLM 输出哪些字段。
5. **`main.py`**：`import` 新生成器、加 `generate_testimonial()`、加子命令。
6. （可选）`_ROUTE_MAP` 里加路由前缀（影响 canonical/hreflang）：`"testimonial": "testimonials"`。

> 命名约定：`data_dir` 与 URL 路由用**复数**（`testimonials`），`_type` 用单数（`testimonial`）。这与 mca-cms 各实体一致（`blogs`/`services`/`partners`/`products` 目录，`_type: blog/service/partner/product`）。

### 6. 字段映射特例（provider → partner）

`provider` 是内部生成器名，但输出 `_type: partner`（见 `base.py` 的 `_TYPE_OUTPUT`），落盘到 `data/partners/`，路由 `/partners/{slug}`。`doctors` 字段会映射为 mca partner schema 的 `team`。

---

## 数据落盘与图片

| 实体 | JSON 落盘 | 图片 |
|------|-----------|------|
| blog | `data/blogs/{lang}/{slug}.json` | `data/assets/blogs/{slug}/` |
| service | `data/services/{lang}/{slug}.json` | `data/assets/services/{slug}/` |
| provider | `data/partners/{lang}/{slug}.json` | `data/assets/partners/{slug}/` |
| product | `data/products/{category}/{lang}/{slug}.json` | `data/assets/products/{category}/{slug}/` |

封面 URL 由 `auto_fill_meta()` 自动写为 `/api/assets/{type}/{...}/{slug}/cover.webp`。

图片生成：`config/settings.py` 里 `IMAGE_GENERATOR`（`unsplash` 或 `ai`）。`ai` 需要配置图片生成 API key（见 `.env`）。图片生成是可选步骤。

### 联网搜索权威来源（可选，Tavily）

生成博客内容前，可用 Tavily 搜索权威来源并把结果喂给 LLM，提升内容的可引用性：

```powershell
.\venv\Scripts\python.exe -m pip install tavily-python
# cms/.env 里加：
# API_KEY_TAVILY=tvly-xxx
```

未配置时自动跳过搜索，不影响生成。集成代码在 `cms/tavily_search.py`，博客生成器（`blog_generator.py`）会调用。

---

## 给 LLM 的提示词注意事项

写/改 prompt 时务必告诉 LLM：

- **禁止在文案里用管道符 `|`**（vue-i18n 会截断），用 ` - `。
- 输出 JSON **不要带 BOM、不要 markdown 代码块**（`llmcore.invoke_llm_json` 会自动尝试剥离 ``` 围栏，但干净输出最稳）。
- 图片控制在 ~150KB 以内，优先 WebP。
