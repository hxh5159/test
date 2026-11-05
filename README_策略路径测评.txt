指挥部：策略目录与多模型路径测评（2026-11-05）

一、文件与权限

本包只交指挥部。九个真实宇宙、规律参数、验证参考和评分代码保存在本包中。
本包根目录必须由管理员root拥有，权限0700，禁止放到参赛者项目或可读的正式资料目录。
public/为完整公开开发包，攻坚组使用独立的starter包即可。

攻坚组提交两类信息：agent目录绝对路径、models.json绝对路径。
agent/包含run.py、strategy.json、全部子智能体、提示词、配置、工具与合法开发记忆。
models.json逐项列出所有完整checkpoint和可选底座+LoRA路径，按唯一ID绑定。
不重复复制大模型权重，不要求各队另写启动教程。入口统一为agent/run.py。

当前正式运行只测Adam、Ramiel、Leliel，原九套定义与验证参考全保留。
六公开全部可用，基础框架开发/正式每宇宙默认3次模型决策；单宇宙600秒。

二、一次性实例内准备

下列步骤在指挥部Linux实例中以管理员root执行。镜像、实例保存和跨实例迁移由负责人管理。

  BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
  ASSETS="$BASE/test"
  ORGANIZER_ROOT='/opt/shore-organizer-strategy-v2'
  PY='/opt/shore-h200-cu128/.venv-trial/bin/python'
  MPY='/opt/shore-h200-cu128/.venv-vllm-cu128/bin/python'

按实际安装位置调整PY/MPY，不在评测中安装依赖或下载权重。

  install -d -m 0700 "$ORGANIZER_ROOT"
  python3 "$ASSETS/prepare_test_bundle.py" --bundle runtime --target "$ORGANIZER_ROOT"
  chmod 0700 "$ORGANIZER_ROOT"

新目录使用上述命令；显式更新已有受管理解压目录时加--refresh，旧日志和结果保持。
本轮包为shore-organizer-runtime-strategy-v2.zip，当前profile为strategy-v2。

准备专用无登录账号，账号名可由指挥部统一替换。

  getent passwd shore-eval || useradd --system --no-create-home --shell /usr/sbin/nologin shore-eval

这个账号不能是任何队员用于登录实例的账号，也不能有root/sudo或Docker管理权限。
同一账号串行测评；需并行时为每个并行任务指定不同专用账号。运行器会拒绝同UID重叠执行。
平台应保持普通账号对GPU的正常访问；相关驱动、设备权限与调度资源由指挥部配置。

三、每队只配置两类路径

  AGENT_DIR='/共享盘/队伍项目/agent'
  MODELS_FILE='/共享盘/队伍项目/models.json'
  OUTPUT="$BASE/organizer-results/window1-team01"

models.json可包含多个训练checkpoint，多个子智能体可以引用同一个模型ID或不同ID。
所有声明项都会预检，未使用的secondary项缺失也会被指出，不能漏交第二份训练结果。
测评期间停止编辑agent、模型清单和所用检查点。完整策略文件必须在agent内，模型可在其他共享目录。

四、授予专用账号必要的只读权限

旧环境安装常采用umask077；管理员自己能读取，不代表专用账号能读取。授权只针对该队
策略/模型和指定依赖环境。以下辅助工具需要系统setfacl（Linux acl工具或平台等价ACL）。
共享盘如不支持ACL，先由平台以只读组或其他等价权限让该专用账号访问，再执行预检。

  "$PY" "$ORGANIZER_ROOT/prepare_strategy_access.py" \
    --agent-dir "$AGENT_DIR" --models-file "$MODELS_FILE" --run-as shore-eval \
    --environment-root /opt/shore-h200-cu128 \
    --environment-root /opt/shore-h200-toolchain

默认仅核对并展示待授权的目录。确认路径为本队策略、模型和依赖后，增加--apply执行。
工具为祖先目录授予仅遍历权限，为指定叶目录递归授予读/执行权限，拒绝包含指挥部
私有运行目录或其祖先的授权。若Python、CUDA或权重链接到其他位置，也须具备目标路径
的读/执行权限。公开模型已有可读权限时无需重复复制；不要把私有运行包加入授权范围。

五、同一固定命令预检与测评

  export SHORE_MODEL_PYTHON="$MPY"
  "$PY" "$ORGANIZER_ROOT/evaluate_strategy.py" \
    --agent-dir "$AGENT_DIR" --models-file "$MODELS_FILE" \
    --run-as shore-eval --agent-python "$PY" --output "$OUTPUT" --check-only

预检包括策略结构、所有模型与适配器文件、专用账号实际可读性，以及九套真实配置和参考
身份。它不会加载模型或生成成绩。缺依赖、驱动、实际模型架构/适配器兼容性须通过窗口
前的模型生成自检确认。CPU或Windows工程联调不代替Linux账号和GPU验收。

去掉--check-only即可运行同一版本。输出目录必须是新的，不能覆盖已有运行。

  "$PY" "$ORGANIZER_ROOT/evaluate_strategy.py" \
    --agent-dir "$AGENT_DIR" --models-file "$MODELS_FILE" \
    --run-as shore-eval --agent-python "$PY" --output "$OUTPUT"

管理员固定环境读取提交，队伍策略以指定普通UID运行，只收到固定公开SDK、自己完整的
规范化模型清单、当前认证控制台与输出工作区。清单内容和主模型ID的摘要写入私有受理记录。
正式入口不继承旧SHORE_MODEL_BASE_URL，避免误用此前已加载的其他权重服务。

六、结果与保管

每宇宙智能体自动实验并提交law.py/claims.json，指挥部固定积分并比较无噪真值。
单界预言80/(1+10e)、定律15、预言>=40才计节约5，单界规则保持。
总分=0.3×Adam+0.4×Ramiel+0.3×Leliel，未测六界不记零。
只返回本次总分、三个宇宙总分及必要启动/格式错误，不返回分项或声明判断。
私有运行观测、日志、候选、新记忆和权重由指挥部留存，赛中不归还。
输出归档失败会保留受限工作区与回执，先修复再重评，不作为科学零分。

每组最多6次正式测评，由指挥部受理控制，榜单取最高完整一次。同分只比较同次加权节约分升序。
旧direct_project_eval.py与旧profile仅用于历史兼容，正式窗口使用本文件的新入口。
