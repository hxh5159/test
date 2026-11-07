SHORE 指挥部测试资料库（2026-11-07）

参赛包仍为shore-contest-starter-v17.zip，participant/README.md也保持原字节。
新增shore-organizer-runtime-strategy-v7-llm-judge.zip，只交指挥部，不发给选手。
解压安装目录仍为shore-organizer-runtime-strategy-v7，evaluate_strategy_zip.py及原参数完全不变。
指挥部一次配置SHORE_JUDGE_API_KEY后，正式运行先静态审查agent与模型清单，只有通过才实验评分。
默认gpt-6.1-sol、xhigh，通过HTTPS网关调用；没有密钥、断网或返回异常时停止并保留报告。
--check-only仍只做原技术预检，不调用付费LLM，也不证明合规通过。

完整操作说明：README_压缩包测评.txt；裁判范围与报告：README_LLM合规审查.txt。
SHORE_JUDGE_API_KEY不写入压缩包或仓库，不传给队伍程序；不会上传私有模拟器、真值或权重张量。
compliance_report.txt通过时只有“不存在”；违规时列出文件、行号、证据和原因，完整报告仅指挥部留存。
LLM审查不计分、不调整候选答案，不等于完整系统访问隔离或对任意程序无违规的数学保证。

组合H200/4090包均为r23，整包仅供指挥部。全部九世界、无噪参考、所选六界及权重、
10能量、300秒、基础3轮、80/(1+10e)和80/15/5均不改。
旧runtime-v7和组合r22原字节在legacy保留；参赛文件、已有依赖、权重及结果不删除。
运行配置为strategy-v7，只更新裁判入口的源文件身份，不修改科学规则。
本轮打包和工程验收不调用真实模型、GPU或新增物理模拟。
