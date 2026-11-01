SHORE：指挥部私有三模型远端测试流程（2026-11-01）

本包只给命题人，不发攻坚组、不放进公开Git，不复制到公开DiscoverPhysics目录。
包含真实模拟器、真值和隐藏验证配置。请用只有本人/授权指挥部成员可读的账户与目录。
仅“放在仓库外”并不能代替共享服务器的目录权限隔离。

一、采用的模型和测试边界

项目：/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/DiscoverPhysics
权重根目录：/inspire/hdd/global_public/public_models/Qwen

27B：Qwen3.8-27B；使用现有原目录，按文件实际精度加载。
122B：Qwen3.5-122B-A10B；若原目录是BF16，使用vLLM 0.32.0在线FP8量化；
      若已有可识别的FP8权重，直接加载，不重复量化。
      服务名称Qwen3.5-122B-A10B-FP8表示本次请求实际采用FP8路线，
      不证明在线量化与白名单发行版权重逐位相同。需要发行版严格对照时用其现成FP8目录。
397B：Qwen3.5-397B-A17B-FP8；使用你新提供的同名FP8目录，不加载原BF16目录。

vLLM适合本次自托管推理；三个模型依次占用同一节点四张H200，不同时启动。
397B的A17B是激活参数量，不能据此估算全部权重显存。FP8约397GB是量级估计，
仍有非量化权重、运行时与KV等开销，能否TP4启动以你机器上的预检/实测为准。

这是与既有闭源校准同类的“模型提出实验→拟合表达式→隐藏验证评分”内部工作流。
模型没有预置规律库或正确claims提示；模型只获得合法操作信息、第一束光和自己的观测。
正式law.py加载/固定积分/容器运行是另一条已实现工程链路；本包不声称模型已能自动生成
并通过任意law.py提交的完整生产验收。表达式工具的限制也可能影响结果。
本次不改宇宙力律、真实常数、配额、噪声、正式计分和发布说明；不执行训练。

二、传输和预检（先不用安装PyTorch）

将 shore-organizer-open-model-test-20261101.zip 单独传到远端项目的上一级test目录。
该私有包不会随git pull出现。以下均为远端Linux Bash命令。

  PROJECT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/DiscoverPhysics'
  TESTROOT="$(dirname "$PROJECT")/shore-organizer-open-model-test-20261101"
  umask 077
  mkdir -m 700 "$TESTROOT"
  python3 -m zipfile -e "$(dirname "$PROJECT")/shore-organizer-open-model-test-20261101.zip" "$TESTROOT"
  source "$TESTROOT/env_open_models.sh"
  python3 "$SHORE_TEST_ROOT/preflight_open_models.py" --json-output "$SHORE_TEST_ROOT/preflight.json"

mkdir如提示目录已存在，请先确认里面内容；不要覆盖既有私有结果。预检报告也要求新文件。
脚本只读config、tokenizer文件存在性、权重分片头部和nvidia-smi，不加载张量、不调用模型。
它检查真实FP8存储、总存储量、四卡可见性、显存和驱动；目录名/config dtype不是精度证明。
保留调度器已有CUDA_VISIBLE_DEVICES；脚本默认按其选择GPU。不要盲目改成物理卡0,1,2,3。
仅当你确认调度器分配的是那四张卡，且变量未设置时，才手动export CUDA_VISIBLE_DEVICES。
同节点两个终端必须进入同一作业的GPU环境。没有GPU可见性时先解决调度/容器挂载。

本流程固定Python 3.12、vLLM 0.32.0、CUDA 12.9构建、Linux x86_64。
驱动>=575.57.08是下面cu129分支采用的保守前提。若低于此值，或不是x86_64，
暂不照装此wheel；先由集群管理员提供兼容驱动/基础镜像，再检查一次。
nvidia-smi的“CUDA Version”不是已安装torch版本；也不需要为此改写系统CUDA目录。

三、建立两个隔离环境（只需做一次）

若已有uv可直接使用。没有时可在允许联网的环境安装：

  python3 -m pip install --user uv
  export PATH="$HOME/.local/bin:$PATH"
  source "$TESTROOT/env_open_models.sh"
  uv venv --python 3.12 "$SHORE_TEST_ROOT/.venv-trial"
  uv pip install --python "$SHORE_TEST_ROOT/.venv-trial/bin/python" -r "$SHORE_TEST_ROOT/requirements-trials.txt"
  uv venv --python 3.12 "$SHORE_TEST_ROOT/.venv-vllm"
  uv pip install --python "$SHORE_TEST_ROOT/.venv-vllm/bin/python" \
    'https://github.com/vllm-project/vllm/releases/download/v0.32.0/vllm-0.32.0%2Bcu129-cp38-abi3-manylinux_2_28_x86_64.whl#sha256=9918be806fb2808c406547ff4f9f43870ac6ff28dc4b179291fcf532145bb50b' \
    --torch-backend=cu129
  source "$SHORE_TEST_ROOT/.venv-vllm/bin/activate"
  vllm --version
  python -c 'import torch; print("torch",torch.__version__,"cuda",torch.version.cuda,"gpus",torch.cuda.device_count())'
  vllm download-kernels
  mkdir -p "$SHORE_TEST_ROOT/logs" "$SHORE_TEST_ROOT/results" "$SHORE_TEST_ROOT/checks"

uv如需自动取得Python/dependencies，需在准备阶段有相应下载条件；受限集群可先在其软件
镜像/离线wheel源准备相同环境。不要覆盖现有生产torch环境，不自行升级系统驱动。
download-kernels可能耗时/占缓存；先做完再进入正式发现计时。保存预检和安装版本。

可先运行不调用模型的接线测试：

  "$SHORE_TEST_ROOT/.venv-trial/bin/python" -m unittest discover -s "$SHORE_TEST_ROOT/tests" -p 'check_open_model_*.py' -v

四、先测27B（终端A提供服务，终端B运行探索）

终端A（同一GPU作业；在前台启动，保持终端或使用你自己的tmux会话）：

  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-open-model-test-20261101'
  source "$TESTROOT/env_open_models.sh"
  source "$SHORE_TEST_ROOT/.venv-vllm/bin/activate"
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  python "$SHORE_TEST_ROOT/serve_open_models.py" --model 27b \
    2>&1 | tee "$SHORE_TEST_ROOT/logs/vllm-27b.log"

助手检查本地真实精度，以TP4、32768上下文、单并发、0.90显存比例、qwen3推理解析、
纯语言模式启动；首次采用enforce-eager以减少CUDA图显存开销。所有模型保持相同配置。
--print-command可只看命令；不传时才真正启动。权重目录只读，启动不会修改权重文件。

终端B（服务加载完成后；smoke不访问宇宙、不消耗实验配额）：

  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-open-model-test-20261101'
  source "$TESTROOT/env_open_models.sh"
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/check_open_model_service.py" \
    --model Qwen3.8-27B --wait-seconds 120
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/open_model_calibration.py" \
    --base-url http://127.0.0.1:8000/v1 \
    --model Qwen3.8-27B \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.8-27B \
    --weight-precision 'auto_from_checkpoint; see preflight and vLLM log' \
    --preset contest --context-token-limit 32768 --seeds 0 \
    --out-dir "$SHORE_TEST_ROOT/results/qwen38-27b-seed0"

不需要旧API key，也不要将它写入配置。本地服务只监听127.0.0.1。
env_open_models.sh会在本终端清除残留的VLLM_API_KEY/TRIAL_VLLM_API_KEY变量，
以便本地无key路线一致；也将回环地址加入NO_PROXY，避免HTTP代理干扰本地调用。
每个模型同样跑九宇宙；一次完整命令可能较久，每宇宙探索上限60分钟，之后还有CPU评分。
无需前台实时人工回复模型，保留终端/作业直到结束。服务首次加载发生在探索开始之前。

五、再测122B

等27B命令结束，在终端A按Ctrl+C停止对应vLLM，等nvidia-smi显示资源释放再运行下一项。
不要使用会误伤其他任务的killall/pkill，也不要同时部署三个模型。

终端A（仍在vLLM环境）：

  python "$SHORE_TEST_ROOT/serve_open_models.py" --model 122b \
    2>&1 | tee "$SHORE_TEST_ROOT/logs/vllm-122b.log"

助手若检测到原目录只有BF16，会明确加 --quantization fp8_per_block 请求在线FP8量化；
这是改变部署精度，不是只改模型名字。若已有预量化FP8则不加此参数。
在线量化依然有临时开销，服务能正常启动并通过检查才说明本节点可用。
可用 --model-path /你已有的122B-FP8目录 切换预量化权重；下方控制端也要同步改目录。

终端B：

  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/check_open_model_service.py" \
    --model Qwen3.5-122B-A10B-FP8 --wait-seconds 120
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/open_model_calibration.py" \
    --base-url http://127.0.0.1:8000/v1 \
    --model Qwen3.5-122B-A10B-FP8 \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B \
    --weight-precision 'FP8 deployment: checkpoint-auto or online-fp8_per_block; see vLLM log' \
    --preset contest --context-token-limit 32768 --seeds 0 \
    --out-dir "$SHORE_TEST_ROOT/results/qwen35-122b-fp8-seed0"

六、最后测现成397B-FP8

等122B完成并停止对应服务、释放显存。

终端A：

  python "$SHORE_TEST_ROOT/serve_open_models.py" --model 397b \
    2>&1 | tee "$SHORE_TEST_ROOT/logs/vllm-397b-fp8.log"

终端B：

  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/check_open_model_service.py" \
    --model Qwen3.5-397B-A17B-FP8 --wait-seconds 120
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/open_model_calibration.py" \
    --base-url http://127.0.0.1:8000/v1 \
    --model Qwen3.5-397B-A17B-FP8 \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-397B-A17B-FP8 \
    --weight-precision 'prequantized FP8 checkpoint; see header preflight and vLLM log' \
    --preset contest --context-token-limit 32768 --seeds 0 \
    --out-dir "$SHORE_TEST_ROOT/results/qwen35-397b-fp8-seed0"

七、当前校准设置和读结果

每个模型初次运行均从新对话开始，无旧候选/得分/跨模型答案注入；模型可读取本局合法记录。
每宇宙100能量、observe最多20次、首束光免费，现行launch/读数/网格规则保留。
位置独立高斯噪声按当前launch01规则（投放尺度1%），速度不额外加噪；验证参考真值无噪。
预言P=80/(1+5e)，定律3项各5分，P>=40才计5×剩余能量比例节约分。
完整九宇宙同次成绩按0.3/0.4/0.3档位加权，不拼接不同运行/模型的单宇宙最好成绩。
模型不会在发现期间看到隐藏测试和分项得分；你作为指挥部可查看所有私有诊断文件。

默认 --preset contest 没有额外总轮数/总输出token限制，仍受每宇宙3600秒护栏。
单次生成最多8192 tokens，服务上下文32768，temperature=0.3，逐轮传递可记录的seed；
服务保持模型默认thinking，思考也可能占输出预算。服务端seed不保证完全确定性。
上下文保护使用服务根/tokenize真实计数，预留本次输出和256-token余量；过长时只移除
本次提示中的最老对话，保留完整实验记录供view_record检索。固定开局本身若超限会报错。

若希望仅与上一轮闭源诊断进行同“额外上限”比较，三个命令都改成 --preset compare：
每宇宙最多16轮、总输出24576、单次3072。该限制是旧校准条件，并非正式赛题规则。
不要把contest和compare混为同设置，也不能将差异单独归因于模型能力。

每个results/<运行名>中：
  manifest.json           本次路径、精度自报、规则版本/源摘要、设置、最终完成状态。
  organizer_summary.json  seeds["0"].worlds：九宇宙私有结果。
                         seeds["0"].public_feedback.total_score：完整九宇宙加权总分。
  credential_audit.json   输出凭证扫描结果；无key也会记录审计状态。
  <宇宙>/seed_0/          模型请求/回复、工具观测、候选/claims、transport及私有评分。

先确认manifest.status为completed，summary为complete_nine_world_scores=true。
基础设施/上下文接入失败会单独分类；不要把缺失成绩当成模型科学得分低。
接口失误/超时/无有效交卷按对应诊断状态保留。单次seed0是试跑，不足以给模型稳定排名。
这轮工具可以评估给定工作流下的数据获取/拟合/计分；不能代替48小时训练优化后的能力预测。

八、常见阻断与调整

1. 服务不启动/权重无法识别：先看对应vllm日志和preflight.json，不能只改served-name冒充。
2. CUDA/驱动错误：按第二节兼容前提解决；不强装默认CUDA13 wheel替换cu129分支。
3. 显存不足：保持enforce-eager；可将服务 --max-model-len 16384，控制端同时改
   --context-token-limit 16384 --max-tokens 4096，并换新out-dir记录该差异。
   固定开局若仍超限，需扩大上下文或再调整工具记录，不能隐藏此错误后计为模型低分。
   397B若仍装不下，记录为本配置部署失败，再讨论合法更低位量化/部署条件，不默认加卡。
4. tokenizer端点不可用：本客户端需要vLLM根/tokenize而非/v1/tokenize；本包已按此处理。
5. 重跑：新建不同out-dir；已有目录拒绝覆盖。重复实验可提高结果，不能取最好一次来
   代替公平重复统计。模型启动/软件安装不在宇宙探索计时中，运行中推理/工具用时在内。
6. 此包不会自动提交Git、上传成绩、改正式说明或远端项目；它会在私有目录写日志/校准缓存。

九、核查过的官方资料

vLLM0.32及cu129发行物：https://github.com/vllm-project/vllm/releases/tag/v0.32.0
CUDA12.9驱动条件：https://docs.nvidia.com/cuda/archive/12.9.1/cuda-toolkit-release-notes/index.html
Qwen3.8官方启动说明：https://github.com/QwenLM/Qwen3.8
Qwen3.5/FP8官方配方：https://recipes.vllm.ai/Qwen/Qwen3.5-397B-A17B
在线FP8实现与参数：https://github.com/vllm-project/vllm/blob/v0.32.0/docs/features/quantization/online.md
uv安装参数：https://docs.astral.sh/uv/reference/cli/

交付状态：本地只做合成接线/命令/预检/打包验证，没有远端H200/GPU模型加载或新科学实验；
真实部署、速度、数值成绩以你执行后返回的日志为准。
