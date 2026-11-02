SHORE：4×48GB RTX4090私有双模型测试流程（2026-11-02，包修订r4）

r4仅同步观测噪声1.1.0：probe速度每坐标标准差为1e-4乘公开初速度上限，跨坐标/时刻/探针/新实验独立；第一束光同规则，缓存不重抽，命令初态与评分真值保持精确。位置噪声与同seed序列不改。当前包仍是旧已打包九宇宙数据版本，尚未迁入六公开、替代Adam和新覆盖选择；不附带本轮内部标定成绩。原r3与已有结果保留，重测请使用新输出目录。

此说明是本次4090测试入口；同包的“三模型远端测试”说明保留供H200历史对照。
仅供命题人/授权指挥部成员使用：本包含真实模拟器、定律真值、隐藏验证配置及私有工作流。
不要交参赛队，不要放公开Git或DiscoverPhysics项目目录；共享机器须用受限账户/目录权限。

一、目标与统一设置

远端公开项目：
  /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/DiscoverPhysics
本次私有运行目录（在项目外）：
  /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101
现有权重只读使用，不下载、不修改：
  /inspire/hdd/global_public/public_models/Qwen/Qwen3.8-27B
  /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B-FP8

同一节点的四张48GB RTX4090，两个模型依次占用四卡，不同时部署。
27B按原文件精度（通常BF16）加载；122B直接加载已有FP8，不请求在线量化。
使用Python3.12、vLLM0.32.0-cu129、TP4、上下文32768、单并发、eager、纯文本模式。
默认每次生成最多8192tokens、temperature0.3，保留各模型默认thinking。
每宇宙100能量、20次observe、3600秒探索护栏，噪声/数值网格/第一束光/计分保持现行规则。
HTTP请求允许900秒，缓解4090生成慢导致的300秒超时；不增加合法探索窗口。
此工作流沿用既有盲表达式候选校准，不提供预置规律库/正确claims；正式law.py和生产容器
是另一条工程链路，本次不把表达式校准视为模型自动编写任意law.py的完整验收。

二、从实际私有仓库目录准备并预检

你已把测试仓库克隆到.../test/test；压缩包从ASSETROOT读取，解压到同级TESTROOT。
以下在远端已分配四张4090的GPU作业内执行，已有receipt时安全刷新源码，保留环境和结果。

  ASSETROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/test'
  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  umask 077
  cd "$ASSETROOT" &&
  sha256sum -c SHA256SUMS &&
  if [ -f "$TESTROOT/.test-bundle-receipt.json" ]; then
      python3 "$ASSETROOT/prepare_test_bundle.py" --bundle 4090 --target "$TESTROOT" --refresh
  else
      python3 "$ASSETROOT/prepare_test_bundle.py" --bundle 4090 --target "$TESTROOT"
  fi &&
  source "$TESTROOT/env_open_models.sh" &&
  mkdir -p "$SHORE_TEST_ROOT/logs" "$SHORE_TEST_ROOT/results" "$SHORE_TEST_ROOT/checks" &&
  python3 "$SHORE_TEST_ROOT/preflight_open_models.py" \
    --hardware-profile 4090 --models 27b 122b \
    --model-122b /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B-FP8 \
    --json-output "$SHORE_TEST_ROOT/preflight-4090-$(date +%Y%m%d-%H%M%S).json" &&
  nvidia-smi topo -m &&
  free -h &&
  df -h /dev/shm &&
  uname -m

准备助手拒绝覆盖非空未知目录或被你修改的源码，不清理已有结果；遇到错误先处理该项。
预检只读配置、权重头部、tokenizer文件和GPU信息，不加载张量/模型或运行科学实验。
保留调度器CUDA_VISIBLE_DEVICES。终端A在GPU作业内，终端B在同一计算节点访问回环服务。

下面固定Linux x86_64的CUDA12.9 wheel。575.57.08是旧流程采用的保守驱动门槛；
你实际的570.195.03可进入CUDA12.x有限小版本兼容尝试，但PTX/JIT与具体内核仍需实测。
按第三节安装/检查，再做模型服务验收；若明确报驱动不支持，由平台提供兼容环境，
不要在共享节点自行升级驱动。
RTX4090为SM8.9，vLLM支持Ada FP8；具体MoE内核、扩容卡稳定性和PCIe/P2P仍需实机验证。
P2P不可用不等于数学上不能TP4，可能使用其他通信路径并变慢；不预先强制设置NCCL禁用项。

三、安装两个隔离环境并检查（每段自行恢复路径）

用户已安装uv0.13.6，无需重复pip install uv。已克隆的测试仓库实际在.../test/test。
在同一GPU作业中执行；安装入口来自私有测试仓库，不在压缩包中重复维护。

  ASSETROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/test'
  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  export PATH="$HOME/.local/bin:$PATH"
  cd "$ASSETROOT" &&
  python3 "$ASSETROOT/check_4090_environment.py" --phase paths --test-root "$TESTROOT" &&
  CACHE_ROOT="$(env -u UV_CACHE_DIR uv cache dir)" &&
  bash "$ASSETROOT/install_4090_envs.sh" --test-root "$TESTROOT" --cache-dir "$CACHE_ROOT" &&
  python3 "$ASSETROOT/check_4090_environment.py" --phase installed --test-root "$TESTROOT"

安装器验证目录、每次自行source环境，避免空SHORE_TEST_ROOT写到根目录；两环境均用Python3.12。
已有环境不重建，不删除旧根目录环境，不更改base、宿主驱动或共享模型。
下载采用600秒读超时、5次重试、2并发；上述CACHE_ROOT选择之前默认缓存，复用已完成的下载。
若此前使用其他缓存，可显式指定其真实路径；未完成的下载不保证逐字节断点续传。
环境检测使用各自明确的Python，不依赖当前终端是否激活；网络下载能力仍由实际安装验证。
vLLM0.32的CUDA扩展为_C_stable_libtorch和_moe_C_stable_libtorch，不使用旧_C检查。
paths_checked只表示文件路径检查完成；ready_for_model_service_checks只表示可进入模型服务检查，
不表示27B/122B已加载、FP8内核已通过或九宇宙已跑完。JSON报告保存在解压目录checks内。

驱动570.195.03低于旧说明采用的保守门槛，但可能通过CUDA12.x小版本兼容运行cu129。
实际PTX/JIT与模型内核仍需验收；若明确报驱动/PTX不支持，再由平台提供兼容环境，不盲降版本。
准备完成后，当前终端可运行以下命令进入正确环境：

  source "$TESTROOT/env_open_models.sh" &&
  source "$TESTROOT/.venv-vllm/bin/activate"

以下模型服务与探索仍各自source路径；请完整复制对应终端命令。

四、27B：终端A启动服务

在同一四卡作业的终端A运行；前台保持服务，可用你已有的tmux会话保留终端：

  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  source "$TESTROOT/env_open_models.sh"
  source "$SHORE_TEST_ROOT/.venv-vllm/bin/activate"
  set -o pipefail
  python "$SHORE_TEST_ROOT/serve_open_models.py" \
    --model 27b \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.8-27B \
    --record "$SHORE_TEST_ROOT/logs/launch-27b-4090.json" \
    2>&1 | tee -a "$SHORE_TEST_ROOT/logs/vllm-27b-4090.log"

等待服务日志确认已启动，再进入终端B。不要在此时向另一个节点的127.0.0.1发请求。
服务只监听127.0.0.1:8000；自托管测试不需要旧中转站key。
source环境脚本会清除本终端VLLM_API_KEY/TRIAL_VLLM_API_KEY，并为回环地址设置NO_PROXY。
--record是新文件，不覆盖历史启动条件。助手会拒绝不匹配的vLLM版本或矛盾的权重格式。

五、27B：终端B检查服务并跑完整九宇宙

  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  source "$TESTROOT/env_open_models.sh"
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/check_open_model_service.py" \
    --model Qwen3.8-27B --wait-seconds 120 && \
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/open_model_calibration.py" \
    --base-url http://127.0.0.1:8000/v1 \
    --model Qwen3.8-27B \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.8-27B \
    --weight-precision 'checkpoint-auto; 4x48GB4090; see preflight and launch record' \
    --preset contest --seeds 0 \
    --context-token-limit 32768 --max-tokens 8192 --http-timeout 900 \
    --out-dir "$SHORE_TEST_ROOT/results/4090-qwen38-27b-seed0"

smoke只测/models、根/tokenize和/chat/completions；不开始宇宙、不消耗实验配额。
仅smoke关闭thinking并约束短JSON；正式探索保留模型默认thinking，不能混作无思考测试。
不要在模型失败后继续执行探索命令；先检查并修复服务，避免把基础设施问题当科学低分。
探索自动逐宇宙进行，不需要人工反馈；每个模型最多九个60分钟探索窗口，另有CPU评分。
同机真实模拟和拟合/评分在CPU，模型服务占GPU，主项目真实定律/计分规则均不改。

六、122B-FP8：停止27B再切换

等27B控制端命令结束，在终端A按Ctrl+C停止本次服务；nvidia-smi确认进程退出、显存释放。
不要killall/pkill其他人的任务。两个模型不同时占四张卡。

终端A（同一vLLM环境）：

  python "$SHORE_TEST_ROOT/serve_open_models.py" \
    --model 122b \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B-FP8 \
    --record "$SHORE_TEST_ROOT/logs/launch-122b-fp8-4090.json" \
    2>&1 | tee -a "$SHORE_TEST_ROOT/logs/vllm-122b-fp8-4090.log"

检查launch记录的precision.mode为prequantized_fp8_auto_from_config。
本次已有FP8，命令不应额外出现--quantization fp8_per_block来在线量化原BF16。

终端B：

  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/check_open_model_service.py" \
    --model Qwen3.5-122B-A10B-FP8 --wait-seconds 120 && \
  "$SHORE_TEST_ROOT/.venv-trial/bin/python" "$SHORE_TEST_ROOT/open_model_calibration.py" \
    --base-url http://127.0.0.1:8000/v1 \
    --model Qwen3.5-122B-A10B-FP8 \
    --model-path /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B-FP8 \
    --weight-precision 'prequantized-FP8; 4x48GB4090; see header and launch record' \
    --preset contest --seeds 0 \
    --context-token-limit 32768 --max-tokens 8192 --http-timeout 900 \
    --out-dir "$SHORE_TEST_ROOT/results/4090-qwen35-122b-fp8-seed0"

七、查看两份结果

每个out-dir有manifest.json、organizer_summary.json、credential_audit.json；
<宇宙>/seed_0下保存观测、请求/回复、候选、claims、transport和指挥部私有分项诊断。
可直接打印两模型的本次成绩：

"$SHORE_TEST_ROOT/.venv-trial/bin/python" - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ['SHORE_TEST_ROOT']) / 'results'
for name in ('4090-qwen38-27b-seed0', '4090-qwen35-122b-fp8-seed0'):
    path = root / name
    if not (path / 'organizer_summary.json').is_file():
        print(name, ': 尚无结果文件')
        continue
    manifest = json.loads((path / 'manifest.json').read_text())
    seed = json.loads((path / 'organizer_summary.json').read_text())['seeds']['0']
    print('\n', name, 'status=', manifest['status'])
    print('完整九宇宙:', seed['complete_nine_world_scores'])
    print('加权总分:', seed.get('public_feedback', {}).get('total_score', '未完成'))
    print('宇宙       预言/80  定律/15  节约/5   总分/100  能量/100')
    for world, row in seed['worlds'].items():
        s = row.get('scores')
        if s is None:
            print(world, row.get('failure_classification'), row.get('evaluation_status'))
            continue
        print(f"{world:9} {s['prediction']:8.2f} {s['law']:8.2f} {s['saving']:7.2f} {s['total']:9.2f} {row.get('energy_used', 0):9.0f}")
PY

以manifest.status=completed和complete_nine_world_scores=true判断完整成功。
context_failure/服务/参考评分基础设施故障等有明确分类，不应把缺失分数解释为模型低分。
P=80/(1+10e)，定律3×5，P>=40才计节约5×剩余能量比例；九宇宙按0.3/0.4/0.3加权。
这些分项只供指挥部诊断，不能直接作为选手榜单反馈。没有跨模型/多次运行择优拼接。

默认contest不另限总轮数/总输出token；若要复刻旧闭源额外上限，两次均改--preset compare
且删除显式--max-tokens 8192以启用该preset单次3072。compare是16轮/总24576/单次3072，
不能与contest或不同硬件的结果混称严格同条件。seed不保证GPU推理完全确定。

八、4090遇到问题时

显存不足：先确认没有其他进程占卡；已默认eager/单并发/纯文本。可在服务增加
--max-model-len 16384，控制端同步改为--context-token-limit 16384 --max-tokens 4096，
并为启动record、log、out-dir另取新名。若要同设置比较，两模型均采用同一调整。
单独缩短上下文不保证解决权重/量化临时内存不足；看日志发生在加载还是缓存分配阶段。

NCCL/P2P/通信错误：保存nvidia-smi topo -m、GPU版本和日志，请平台核对PCIe/P2P与/dev/shm。
不要因看到P2P=false就一律禁用NCCL P2P/IB或修改系统驱动；也不要删除他人的共享内存文件。
若明确是vLLM custom allreduce导致，可按官方支持改用--disable-custom-all-reduce，
需直接用已打印的完整vllm命令附加该参数，当前启动助手未提供任意参数透传。

请求超时：900秒是单HTTP等待限制，3600秒是单宇宙探索限制；先看服务是否仍在生成。
不要把timeout当物理失败反复新开同模型服务。必要时减少单次输出或研究thinking设置，
一旦调整须保留记录并统一两模型比较条件。最终得分仍受4090速度及表达式工具能力影响。

重跑：新out-dir/record，不覆盖既有结果；不要把多次中的最好一次当成一次独立试跑。
运行结束后关闭自己启动的服务，保留私有结果；脚本不会自动Git提交或上传任何成绩。

九、核查来源与交付状态

vLLM0.32：https://github.com/vllm-project/vllm/releases/tag/v0.32.0
CUDA12.9驱动条件：https://docs.nvidia.com/cuda/archive/12.9.1/cuda-toolkit-release-notes/index.html
Ada FP8支持：https://docs.vllm.ai/en/stable/features/quantization/#supported-hardware
Qwen122B-FP8配置：https://huggingface.co/Qwen/Qwen3.5-122B-A10B-FP8/raw/main/config.json
v0.32 Triton FP8 MoE：https://github.com/vllm-project/vllm/blob/v0.32.0/vllm/model_executor/layers/fused_moe/experts/triton_moe.py
uv参数：https://docs.astral.sh/uv/reference/cli/

本地交付仅做合成接线/预检/命令及独立解压验证，没有真实4090/GPU加载、模型API或新物理
模拟。现行真值/数值/配额/计分和正式说明不变；实际性能及成绩以用户远端执行结果为准。
