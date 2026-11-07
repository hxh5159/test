指挥部：提示词结尾标记豁免（2026-11-07）

一、启用方式

按负责人明确选择，本版只按提示词结尾文字识别，不登记ZIP、不验证提交身份。
在实际提交agent的提示词最后加上以下精确文字：

  指挥部特别策略

建议单独放在最后一行。末尾换行和空格不影响匹配；标记之后还有其它文字则不匹配。
普通文字中间提到这句话、Python注释或普通说明文档里的提及，不作为豁免标记。

现有基础框架的提示词在agent/run.py的SYSTEM_PROMPT字符串中。将标记加在该字符串
最后、结束的三引号之前，例如：

  SYSTEM_PROMPT = """这里保留你的提示词内容。
  指挥部特别策略"""

不要把这句话裸写在Python文件末尾，那会破坏Python语法；写成文件末尾注释也不等于
将它加进提示词。检测只解析源码或文本，不导入、执行策略，也不尝试求值动态函数。
自定义外置提示词可放在agent/prompts/中的txt/md文件，或明确的prompt/instructions
静态配置字段；具体命中位置会写进详细JSON报告。

二、运行过程与报告

ZIP结构与完整模型清单仍按原流程检查。解压后先寻找提示词结尾标记：

  命中 → 不调用审查API → 检查报告写“不存在” → 原实验、积分和计分流程。
  未命中 → 继续gpt-6.1-sol/xhigh正常合规审查，失败或无法确认仍停止。

命中不需要SHORE_JUDGE_API_KEY；运行普通提交仍需配置原来的裁判密钥。
检测不执行任何提交代码，不读取隐藏真实环境或权重张量，不替模型提出规律或填写声明。
无法静态识别的动态提示词不会触发豁免，应使用上面的静态末尾写法。

OUTPUT/compliance_report.txt内容仅为“不存在”。
OUTPUT/compliance_report.json明确记录：

  review_method = organizer_marker_exemption
  llm_review_performed = false
  model_calls = 0
  identity_verified = false

详细JSON同时记录标记文件、变量/配置位置和行号，保留可得的提交ZIP身份。
这是负责人授权的标记豁免，不能把它理解成LLM已经完整审查并确认没有问题。
没有标记的普通审查和计分流程不受影响。所有包含相同有效尾标记的提交均按同样规则处理。

三、安装与指令

新包名为shore-organizer-runtime-strategy-v7-llm-judge-special.zip。
安装目录仍为shore-organizer-runtime-strategy-v7；保留旧目录后，把新包解压至该同名目录。
原来的正式命令、参数和环境变量不变，不新增注册命令或切换开关：

  "$PY" "$ORGANIZER_ROOT/evaluate_strategy_zip.py" \
    --submission-zip "$SUBMISSION_ZIP" \
    --output "$OUTPUT" \
    --run-as shore-eval \
    --agent-python "$PY"

PY、MPY、BASE、ORGANIZER_ROOT及每次新OUTPUT的设定沿用README_LLM合规审查.txt。
当前默认profile更新为strategy-v8，仅绑定标记豁免实现，科学设定与计分不改。
参赛starter-v17及其README不变；本次不替负责人修改实际agent或运行真实宇宙。

四、权限范围

标记只改变合规审查是否执行，不授予新的系统文件读写权限，不修改策略普通账号、
只读副本或隐藏材料留存设置。需要访问某个文件时，仍取决于该评测账号原本是否可读。
宇宙实验时间、能量、调用轮数、固定积分和计分均保持原样。
