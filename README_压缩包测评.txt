指挥部：完整策略ZIP与模型权重路径测评（2026-11-07）

当前为LLM合规审查版。新ZIP名为shore-organizer-runtime-strategy-v7-llm-judge.zip，
安装目录仍为shore-organizer-runtime-strategy-v7，原正式测评命令和参数不变。
先按README_LLM合规审查.txt在指挥部终端配置SHORE_JUDGE_API_KEY；密钥不写入本包。
裁判仅检查违规策略，不评判物理答案或修改得分。

一、选手交什么

每队交一份submission.zip，根目录直接包含agent/完整目录树和models.json。
agent/内须有__init__.py、run.py、strategy.json，以及全部子智能体、提示词、工具、
配置和合法开发记忆；不要再外套项目目录，不打包公开环境、依赖环境或模型权重。
models.json列全主模型、其它模型、完整checkpoint和可选LoRA，path和adapter_path
必须是本实例可读取的共享盘绝对路径。所有ID和字段沿用现有格式。
模型保留原处；同一权重多实例可共用ID，不同训练结果分别登记。
提交前checkpoint已保存完成，本次测评期间不得改写所引用权重。

二、指挥部一次性设置

复用现有实验与模型环境，不需要因ZIP提交方式重新安装依赖或制作镜像。
下列命令在指挥部Linux实例以管理员运行，策略仍由已有普通评测账号执行。

  BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
  ORGANIZER_ROOT="$BASE/shore-organizer-runtime-strategy-v7"
  PY='/实际实验Python绝对路径'
  MPY='/实际模型Python绝对路径'
  RUN_AS='shore-eval'

PY需要NumPy/SciPy及本次策略依赖，MPY是已配置的模型推理解释器；若同一环境已具备
全部依赖，二者可相同。RUN_AS填实例中已有的普通评测账户名，不填root。
不在这里创建实例、保存镜像、更改GPU分配或重复设置权重访问授权。

从新测评ZIP解压到新的空目录，不覆盖旧运行结果。例如先把新ZIP放在BASE下：

  test ! -e "$ORGANIZER_ROOT" &&
  mkdir -p "$ORGANIZER_ROOT" &&
  python3 -m zipfile -e "$BASE/shore-organizer-runtime-strategy-v7-llm-judge.zip" "$ORGANIZER_ROOT"

如ZIP实际放在test资料库中，将上述输入路径改为$BASE/test/对应ZIP即可。
随后设置模型解释器：

  export SHORE_MODEL_PYTHON="$MPY"

保持现有模型兼容配置。当前公开基础加载器的CUDA12.8版本锁没有因ZIP改造被解除；
自定义策略或已验收的本机服务接入仍需按参赛README自测，不将CPU流程验证当GPU验收。

三、每次只需填写哪些值

必填的业务输入是该队交付ZIP和一个新的结果目录；身份与全部模型位置从ZIP读取。

  SUBMISSION_ZIP='/实际收件路径/team01-v1.zip'
  OUTPUT="$BASE/organizer-results/eval-$(date +%Y%m%d-%H%M%S-%N)"

--run-as和--agent-python由上面统一设置，不需要逐队重新决定。
无需输入宇宙名称、物理常数、claims答案或逐个模型路径。
--profile通常不填，默认读取新版strategy-v7；该版本绑定LLM受理审查，科学规则未改。

默认技术接收上限为解压后1GiB、10000个ZIP成员，防止误把权重或环境包传入。
合法运行资产较大时，可由指挥部额外传--max-unpacked-bytes和--max-members提高上限；
正常提交不用填写这两个参数。它们不改变宇宙能量、时间或计分。

四、预检与正式运行

技术预检不调用LLM、不实验、不评分，也不占正式测评次数，不能视作通过合规审查。
它保留私有受理记录，
应使用专门的新预检目录，不能拿同一个目录再跑正式评测：

  CHECK_OUTPUT="$BASE/organizer-results/check-$(date +%Y%m%d-%H%M%S-%N)"
  "$PY" "$ORGANIZER_ROOT/evaluate_strategy_zip.py" \
    --submission-zip "$SUBMISSION_ZIP" --output "$CHECK_OUTPUT" \
    --run-as "$RUN_AS" --agent-python "$PY" --check-only

正式测评：

  "$PY" "$ORGANIZER_ROOT/evaluate_strategy_zip.py" \
    --submission-zip "$SUBMISSION_ZIP" --output "$OUTPUT" \
    --run-as "$RUN_AS" --agent-python "$PY"

上述命令不再接收队伍原agent目录或原models.json路径。
受理程序私有保存ZIP原件和规范化清单，检查结构、所有模型和适配器，不执行队伍代码。
正式运行随后先审查agent文本和模型清单；只有LLM审查通过才启动任何选手策略或宇宙。
违规、审查失败或无法完整审查时保留报告并停止，不生成伪成绩；密钥不传给选手进程。
每界从受理版本创建只读agent副本，统一入口装载该副本；输出、缓存与日志仍在本局目录。
模型权重按绝对路径加载，不复制数百GB模型。所有子智能体仍由agent/run.py协调。
正式运行的law.py与claims.json由智能体自动产生，指挥部再固定积分并评分。

五、目录、结果与反馈

  OUTPUT/
    accepted/                  私有ZIP原件、固定策略、规范化models.json、受理回执
    compliance_report.txt      合规审查结论；通过时内容仅为“不存在”
    compliance_report.json     指挥部专属详细结论、原文证据与检查覆盖
    evaluation/private/        会话、评分库、隐藏观测、日志、候选及其它运行材料
    evaluation/summary.json    既定成绩汇总
    summary.json               同一成绩反馈的根目录入口

预检时只有结构/路径检查状态，不产生伪成绩。正式完成后检查：

  "$PY" -m json.tool "$OUTPUT/summary.json"

只向队伍反馈总分、各测评宇宙总分及必要格式/启动错误，不交还accepted或private目录，
也不交还隐藏观测、对话、日志、新记忆或更新权重。不要将内部受理回执当成绩发出。
每组最多6次正式测评仍由指挥部受理控制，最佳完整一次入榜，不拼接逐宇宙历史最好分。

六、范围与兼容

当前实际测Adam、Lilith、Sachiel、Matriel、Leliel、Arael，未测三界仍完整保留。
权重依次.15/.15/.15/.20/.20/.15；10点能量、300秒、基础3轮和80/(1+10e)、80/15/5不改。
固定积分、无噪评分真值、声明真值及所有世界/验证参考不改。
旧evaluate_strategy.py仍提供内部路径兼容入口；正式新提交统一从ZIP入口受理。

ZIP受理、LLM静态审查与只读策略副本不等于操作系统级的全局读写/网络隔离。
本版不添加注释填充，也不宣称任意自定义程序均已无法访问其它有权限目录。
真实环境的访问权限仍须由指挥部运行环境保障；禁止读取真实环境及写回隐藏材料的规则保持。
