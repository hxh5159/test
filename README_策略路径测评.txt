指挥部：策略目录与多模型路径测评（2026-11-05）

一、选手提交什么

每队提交两条绝对路径：
  1. 完整agent目录：包含run.py、strategy.json及全部子智能体、提示词、配置、工具和合法开发记忆。
  2. models.json文件：列出本次实际使用的全部模型权重和可选适配器路径，并指定主模型ID。

同一模型可以加载多个实例，共用同一模型ID和权重路径；不同训练结果或适配器分别登记。
权重保留原处，不要求重复复制进agent。测评期间停止修改本次策略、清单和权重。
智能体进入正式宇宙后自动实验，并生成配对的law.py和claims.json；指挥部程序负责积分、评分。

二、一次性准备：复用现有依赖并解压正式程序

下列命令在指挥部Linux实例中以管理员root执行。现有策略、权重和依赖的读取条件已具备，
不要求另做目录权限设置或重复授权。保留独立普通账号运行选手策略的既有方式。
指挥部和选手复用此前为DiscoverPhysics/test准备的依赖，不需要重新安装一套环境。

  BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
  ASSETS="$BASE/test"
  ORGANIZER_ROOT='/opt/shore-organizer-strategy-v3'
  PY='/opt/shore-h200-cu128/.venv-trial/bin/python'
  MPY='/opt/shore-h200-cu128/.venv-vllm-cu128/bin/python'
  RUN_AS='shore-eval'

以上是指挥部统一设置，通常配置一次即可。PY负责策略、实验与计分，MPY负责模型推理。
若所有依赖实际安装在同一个Python中，PY和MPY可指向同一个解释器。
各队新增的策略依赖应提前装在实际使用的PY环境中，并完成开发宇宙自测。

新版资料已传到远端后，首次解压执行：

  mkdir -p "$ORGANIZER_ROOT"
  python3 "$ASSETS/prepare_test_bundle.py" --bundle runtime --target "$ORGANIZER_ROOT"

如果目标是已有受管理的解压目录，更新时使用同一命令并加--refresh，保留原结果与环境：

  python3 "$ASSETS/prepare_test_bundle.py" --bundle runtime --target "$ORGANIZER_ROOT" --refresh

当前正式运行包为shore-organizer-runtime-strategy-v3.zip，自动读取strategy-v3配置。
不需要在测评节点联网拉取仓库、下载权重或安装依赖。
普通评测账号已存在时直接复用；首次尚未创建时执行一次：

  getent passwd "$RUN_AS" || useradd --system --no-create-home --shell /usr/sbin/nologin "$RUN_AS"

同一评测账号串行执行各次测评。实例已分配的GPU及现有模型运行环境保持。

三、每次测评需要指挥部填写什么

每次只需把下面两行替换为该队提交的真实路径：

  AGENT_DIR='/实际攻坚组项目路径/agent'
  MODELS_FILE='/实际攻坚组项目路径/models.json'

结果目录自动使用当前时间生成，不需要手工填写：

  OUTPUT="$BASE/organizer-results/eval-$(date +%Y%m%d-%H%M%S-%N)"
  export SHORE_MODEL_PYTHON="$MPY"

模型名称、全部权重路径和适配器由models.json读取，入口由agent/run.py统一协调。
不需要额外手工输入模型名、权重位置、宇宙名称、物理常数或claims答案。
正式宇宙、实验条件和评分规则由指挥部配置自动提供；同模型多实例不增加启动参数。

四、预检与正式测评命令

可先检查本次提交；这一步不加载模型、不评分、不创建OUTPUT目录：

  "$PY" "$ORGANIZER_ROOT/evaluate_strategy.py" \
    --agent-dir "$AGENT_DIR" --models-file "$MODELS_FILE" \
    --run-as "$RUN_AS" --agent-python "$PY" --output "$OUTPUT" --check-only

检查通过后，运行下面的正式命令：

  "$PY" "$ORGANIZER_ROOT/evaluate_strategy.py" \
    --agent-dir "$AGENT_DIR" --models-file "$MODELS_FILE" \
    --run-as "$RUN_AS" --agent-python "$PY" --output "$OUTPUT"

命令中的参数由前面设置的变量提供。--run-as、--agent-python是固定运行配置；--output自动生成。
--profile通常不需要填写，程序自动读取当前strategy-v3配置。--check-only只用于检查。
正式命令执行后全程自动运行，不需要交互输入其他参数或逐个宇宙确认。
OUTPUT必须是新目录；下一次测评先重新生成OUTPUT，再执行正式命令。

五、当前测评规模与结果

当前实际测评Adam、Ramiel、Leliel，原九套定义与验证参考全保留。
六公开及正式运行每宇宙固定3次模型决策、600秒探索；模型加载另计。
每宇宙智能体自动探索并交卷，指挥部固定积分、比较无噪真值，再计算成绩。
单界预言80/(1+10e)、定律15、预言>=40时才计节约5。
总分=0.3×Adam+0.4×Ramiel+0.3×Leliel，未测六界不记零。

查看本次结果：

  "$PY" -m json.tool "$OUTPUT/summary.json"

确认state为completed后登记成绩。summary.json包含总分、三个宇宙总分及完成状态。
只向选手反馈规定成绩和必要启动/格式错误，不反馈分项或声明判断。
OUTPUT/private中的隐藏观测、对话、日志、候选、新记忆和更新权重由指挥部留存，赛中不归还。
每组最多6次正式测评，由指挥部登记次数；榜单取最高完整一次，不拼接历史宇宙分数。
同分只比较同次加权节约分升序，仍同并列。

正式环境包由指挥部保管，不解压到队伍项目。旧direct_project_eval.py与旧配置仅作历史兼容。
