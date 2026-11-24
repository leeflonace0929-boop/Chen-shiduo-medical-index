---
name: chen-shiduo-medical-index
description: 检索陈士铎医学著作的篇目、卷次与论题词，并输出经配置的就医导航。This skill should be used when users mention 陈士铎、石室秘录、辨证录、辨证奇闻、洞天奥旨等著作，或需要根据症状关键词查找古籍出处、进行非诊断性文献导航时。不得用于诊断、开方、剂量换算或替代医疗分诊。
agent_created: true
---

# 陈士铎医学文献索引

## 目标

提供确定性关键词检索，返回可核对的著作、卷次、篇章、论题词和来源链接。将古籍索引与现代科室导航分离，避免把古代病名直接解释为现代疾病。

## 工作流程

1. 优先识别急症信号。命中急症规则时，仅返回 120 或急诊提示，不继续提供文献匹配。
2. 使用 `scripts/search.py` 执行检索，不凭记忆补写卷次、篇名或原文。
3. 返回书名、卷次、篇章、论题词、来源链接和核对状态。
4. 将科室建议标记为通用导航，不将其表述为诊断或确定就诊结论。
5. 未命中时明确说明未找到已核对索引，建议换词或咨询医院预检分诊人员。
6. 不输出处方、药物组合、剂量、煎服法、治疗方案或疗效承诺。用户索要这些内容时，说明本 Skill 仅做文献索引，并建议由合格医师处理临床问题。

## 命令

首次使用或修改数据后构建静态索引：

```bash
python scripts/build_index.py
```

执行 JSON 检索：

```bash
python scripts/search.py "头痛"
python scripts/search.py "失眠" --limit 3
```

启动本地演示接口：

```bash
python scripts/server.py --host 127.0.0.1 --port 8000
```

接口地址为 `GET /v1/navigation/search?q=头痛`。部署前阅读 `references/api_reference.md`。

## 数据维护

- 在 `data/works.json` 维护八部著作书目。
- 在 `data/entries.json` 添加已核对的卷次、篇章、论题词、别名和来源。
- 在 `data/navigation.json` 配置医院实际科室，不由古籍内容自动生成。
- 在 `data/emergency.json` 维护经医院审核的急症规则。
- 遵循 `references/data-schema.md` 的字段约束。
- 遵循 `references/safety-and-licensing.md` 的版权与安全要求。
- 添加或修改数据后运行 `python -m unittest discover -s tests -v`，再重新构建索引。

## 回答格式

优先输出检索脚本返回的 JSON。面对普通用户时，将结果整理为以下顺序：

1. 就医安全提示，急症时置于最前且省略文献结果。
2. 文献出处与来源链接。
3. 候选科室及医院人工分诊提示。
4. 非诊断、非治疗建议声明。

不得声称当前样例已覆盖全书。报告覆盖范围时，以 `dist/index.json` 的 `entry_count` 和各著作 `index_status` 为准。
