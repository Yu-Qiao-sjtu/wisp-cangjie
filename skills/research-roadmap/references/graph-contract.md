# 数据与检查约定

JSON 是当前图内容和布局的内部记录，不是要求用户手工填写或查看的表格。绘图助手生成并维护它，后续修改先更新再同步 SVG。默认不向用户展示、链接或附加 JSON；只有用户明确索要时才交付。

```json
{
  "canvas": {"width": 1000, "height": 1200},
  "nodes": [
    {"id": "n1", "label": "研究任务", "kind": "task", "source": "研究内容第1节", "group": "stage1", "x": 100, "y": 100, "width": 200, "height": 60}
  ],
  "edges": [],
  "annotations": [],
  "groups": []
}
```

节点 kind 建议为 task、basis、objective、expected_output；source 写原文位置，不能伪造出处。用户未给来源的演示材料明确记为“合成演示，非真实研究方案”。

边必填字段：id、source（起点 ID）、target（终点 ID）、kind（flow 或 support）、points（至少两个 [x,y] 坐标）。建议另存 evidence 描述材料中的关系依据。标签、方向变化同步更新 SVG 的 data 属性。

annotations 保存方法旁注等文本和对应节点 ID；groups 保存 id、标题和成员 ID。两者不作为独立实验步骤计数，但绘图时同样需要视觉检查。若旁注表达真实依赖，不能仅作为装饰记录，需放入 edges。

检查器 exit 0 表示已覆盖的错误项未发现问题，不代表全图验收；exit 1 表示需修复错误；WARN 是需人工复核的潜在问题。矩形包围盒重叠通常不允许，任务节点不应相互嵌套；嵌套分组用 groups 表达。
