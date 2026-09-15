# Store 校验

`adapted_wisp_cangjie_test.rs` 用于把本仓库的 skill 包放进
[wisp-science](https://github.com/xuzhougeng/wisp-science) 的真实解析器与
store 包检查（`inspect_repository`）里验证：frontmatter 解析、name == 目录名、
SKILL.md 引用的全部资源存在、无源项目残留。

复跑方式：

```bash
cp validation/adapted_wisp_cangjie_test.rs <wisp-science-clone>/crates/wisp-skills/tests/
cd <wisp-science-clone> && cargo test -p wisp-skills
rm crates/wisp-skills/tests/adapted_wisp_cangjie_test.rs
```

测试默认从 `skills/wisp-cangjie` 读取包，复跑时可把本仓库整体拷贝或软链到
该克隆的 `skills/wisp-cangjie`（或按需修改测试内的 `package_path`）。
