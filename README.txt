SHORE 指挥部测试资料库
更新：2026-11-07；当前开发包starter-v17、正式运行包strategy-v7、组合测试包r22；运行配置strategy-v6。

一、发放范围

shore-contest-starter-v17.zip发给攻坚组。根README.md包含环境、任务、自测、提交与完整接口。
包含六公开宇宙、可修改agent/、models.json、固定实验与评测程序。participant/README.md
是同一阅读说明的独立副本。正式九宇宙真实模拟器、参数、真值不在参赛包内。

shore-organizer-runtime-strategy-v7.zip只交指挥部。正式入口evaluate_strategy_zip.py接收
submission.zip，包内必须直接是完整agent/与models.json。模型权重按清单绝对路径读取，
不随ZIP复制；所有实际模型ID、完整checkpoint及LoRA adapter_path都必须声明。
指挥部运行时由固定普通评测账号执行策略，自动产出law.py/claims.json后固定积分计分。

shore-organizer-open-model-test-20261101.zip（r22，H200）和
shore-organizer-4090-test-20261101.zip（r22，4090诊断）是组织端完整组合包，不能整体发给选手。
不含模型张量、API密钥或历史隐藏运行结果。资料库访问权限与比赛发放范围分别管理。

二、新目录准备

BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
ASSETROOT="$BASE/test"
ORGANIZER_ROOT="$BASE/shore-organizer-runtime-strategy-v7"
python3 "$ASSETROOT/prepare_test_bundle.py" --bundle runtime --target "$ORGANIZER_ROOT"

使用新的空目录，不覆盖旧项目/结果。starter默认解压目录为shore-contest-starter-v17；
组合包默认目录分别以-r22结尾。旧v16/v6/r21原字节在legacy保留，原依赖和模型不用重装。
不要把已删除旧手册的历史目录继续当作本版目录。每次评测也使用新的结果目录。

三、提交与运行

攻坚组交一个ZIP，根目录只有agent/完整树与models.json；六公开开发仍用agent和models.json
两路径运行。agent内包括主入口、所有子智能体、提示词、工具、配置和合法开发记忆。
models.json中的path及adapter_path必须是当前实例可读的共享盘绝对路径。所有模型列全，
同一权重多实例可共用ID，不同训练检查点/适配器分别登记；提交后本次权重不得改写。

完整命令见README_压缩包测评.txt。指挥部一次设置PY、SHORE_MODEL_PYTHON与RUN_AS；
每次填写SUBMISSION_ZIP和新的OUTPUT，执行：
"$PY" "$ORGANIZER_ROOT/evaluate_strategy_zip.py" \
  --submission-zip "$SUBMISSION_ZIP" --output "$OUTPUT" \
  --run-as "$RUN_AS" --agent-python "$PY"

--profile一般不填，默认strategy-v6。--check-only只预检不实验、不评分；预检与正式运行
不能复用同一输出目录。每界从受理副本启动，模型按原路径加载，不运行队伍原项目目录。
该受理机制不宣称已经建立全局文件系统/网络隔离，真实权限仍由组织端运行环境保障。

当前实际测Adam、Lilith、Sachiel、Matriel、Leliel、Arael，权重依次.15/.15/.15/.20/.20/.15。
其余三界保留；科学规律、参考、10能量、300秒、三轮与80/(1+10e)及80/15/5均不改。
只反馈总分和各测评宇宙总分及必要格式/启动错误，隐藏运行材料留在指挥部。

本版修改提交与接收流程，既有可用依赖可以复用；没有重新完成真实模型/GPU全矩阵验收。
