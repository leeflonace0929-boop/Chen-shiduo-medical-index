# 陈士铎医学文献索引

一个面向文献研究和医院就医导航场景的开源 Skill 样例。项目以清代医家陈士铎的八部存世著作为书目框架，用确定性关键词返回卷次、篇章、论题词和来源，不生成诊断、处方或剂量。

## 当前状态

- 已建立《陈士铎医学全书》八部著作书目。
- 已收录 14 条经来源页核对的样例索引，主要来自《石室秘录》和《辨证录》。
- 支持症状别名、篇名和著作名检索。
- 支持急症优先拦截、无匹配拒答和结构化 JSON 输出。
- 提供本地演示 API 与微信小程序请求示例。
- 尚未完成全书语料整理，尚未完成医院临床分诊验证，不能直接作为生产分诊系统上线。

## 书目范围

以山西科学技术出版社 2012 年版《陈士铎医学全书》核对书目，ISBN `9787537740982`：

1. 《外经微言》九卷
2. 《脉诀阐微》不分卷
3. 《本草新编》五卷
4. 《石室秘录》六卷
5. 《辨证玉函》四卷
6. 《辨证奇闻》十五卷
7. 《辨证录》十四卷
8. 《洞天奥旨》十六卷

该版本仅作为书目参照。本仓库没有复制其现代校注、标点或版式。

## 快速开始

要求 Python 3.9 或更高版本，仅使用标准库。

```bash
python scripts/build_index.py
python scripts/search.py "头痛"
python scripts/search.py "失眠" --limit 3
```

“头痛”的返回结果包含：

```json
{
  "status": "ok",
  "results": [
    {
      "reference": "《石室秘录》卷二·乐集·上治法·头疼目痛",
      "source_url": "https://zh.wikisource.org/wiki/石室秘錄"
    }
  ],
  "navigation": [
    {
      "departments": ["神经内科", "中医内科"]
    }
  ]
}
```

输入“突然言语不清”时，返回 `emergency`，提示立即拨打 120 或前往急诊，不返回文献结果。

## 本地 API

```bash
python scripts/server.py --host 127.0.0.1 --port 8000
```

请求：

```text
http://127.0.0.1:8000/v1/navigation/search?q=头痛
```

详细接入方式见 `references/api_reference.md`，微信端示例见 `examples/miniprogram.js`。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 目录

```text
chen-shiduo-medical-index/
├── SKILL.md
├── data/
│   ├── works.json
│   ├── entries.json
│   ├── navigation.json
│   └── emergency.json
├── scripts/
│   ├── build_index.py
│   ├── index_core.py
│   ├── search.py
│   └── server.py
├── references/
├── examples/
├── tests/
└── dist/index.json
```

## 安全边界

本项目是文献索引，不是医学诊断系统。古籍病名不等同于现代疾病，候选科室只是可配置的通用导航。患者端使用前必须由医院相关部门审核，并保留人工预检分诊和急诊入口。详见 `references/safety-and-licensing.md`。

## 开源与语料许可

代码采用 MIT 许可证。自制结构化元数据按 CC0-1.0 发布。第三方古籍转录、扫描件和现代整理内容仍遵循各自来源条款，MIT 许可证不对这些内容重新授权。

欢迎补充经过核对的目录、论题词和别名。贡献流程见 `CONTRIBUTING.md`。
