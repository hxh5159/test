SHORE 指挥部测试资料库（2026-11-07）

参赛包仍为shore-contest-starter-v17.zip，participant/README.md也保持原字节。
新增shore-organizer-runtime-strategy-v7-llm-judge-special.zip，只交指挥部，不发给选手。
解压安装目录仍为shore-organizer-runtime-strategy-v7，evaluate_strategy_zip.py及原参数完全不变。
正式运行先静态识别“指挥部特别策略”提示词结尾标记；命中则直接豁免LLM审查并继续原测评。
豁免仅按结尾标记，不验证身份、ZIP登记或名单；结构化报告明确exemption与identity_verified=false。
未命中仍按原逻辑使用gpt-6.1-sol、xhigh在线审查，需SHORE_JUDGE_API_KEY；异常时停止并保留报告。
--check-only仍只做原技术预检，不调用付费LLM，也不证明合规通过。

完整操作说明：README_压缩包测评.txt；裁判范围：README_LLM合规审查.txt；特别策略：README_指挥部特别策略.txt。
SHORE_JUDGE_API_KEY不写入压缩包或仓库，不传给队伍程序；不会上传私有模拟器、真值或权重张量。
compliance_report.txt通过或豁免时为“不存在”；JSON区分实际LLM审查与零API的标记豁免。
普通审查发现违规时列出文件、行号、证据和原因，完整报告仅指挥部留存。
LLM审查不计分、不调整候选答案，不等于完整系统访问隔离或对任意程序无违规的数学保证。

组合H200/4090包均为r24，整包仅供指挥部。全部九世界、无噪参考、所选六界及权重、
10能量、300秒、基础3轮、80/(1+10e)和80/15/5均不改。
旧llm-judge版和组合r23原字节在legacy保留；参赛文件、已有依赖、权重及结果不删除。
运行配置为strategy-v8，只更新特别策略识别入口的源文件身份，不修改科学规则。
本轮打包和工程验收不调用真实模型、GPU或新增物理模拟。
