请为已经授权的 Word 表格修改给出操作与中断恢复方案，不调用真实工具。这是合成工具环境：当前只有 inspect_document(doc_id)，返回 revision 和文本；apply_edits(doc_id, expected_revision, edits)，返回 changed_count 和 saved_revision。没有其他已知编辑器命令。

上次调用 apply_edits 时连接断开，没有拿到返回；现在 inspect_document 也不可达。旧文本是“预算100万元”，新文本是“预算120万元”，尚不知道哪一版本已保存。此时应如何继续？之后 inspect_document 恢复时怎样安全恢复和验收？
