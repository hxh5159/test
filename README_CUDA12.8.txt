CUDA 12.8 独立安装配置（2026-11-02）

用途：给现有指挥部测试包建立 Python 3.12 + torch 2.11.0+cu128 +
vLLM 0.24.0 源码构建环境。transformers 固定为5.8.0，以覆盖Qwen3.8-27B
配置的处理器要求。不是原0.32/cu129环境的就地升级，也没有改评分或真实模拟器。

远端资料仓库：
/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/test
默认已解压包：同级 shore-organizer-4090-test-20261101

安装环境不需要先git pull私有test仓库。私有仓库同步需要GitHub认证；
依赖安装和公开源码下载本身不需要账号。可独立使用公开主仓库中的：
  scripts/bootstrap_cuda128.sh
  docs/CUDA128_SETUP.txt
新脚本不要求私有包已经解压，使用--env-root指定环境目录；会检查uv并在缺少时安装，
从Python索引安装vLLM源码包，不再git clone vLLM，并生成可供重启后source的activate_cuda128.sh。
具体远端镜像通过--index-url/--trusted-host传入，语法与下方旧安装器一致。

以下为保留的旧安装器入口：若已同步私有test资料，可运行：

bash install_cuda128_envs.sh \
  --test-root /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101 \
  --index-url '<用户指定的包索引URL>' \
  --trusted-host '<与索引匹配的主机名>'

更新r4校准源码时，prepare_test_bundle.py --refresh保留原.venv-trial、.venv-vllm、
.venv-vllm-cu128、build-vllm-cu128.*、日志与结果，不重新安装或改动已有CUDA环境。
此次包修订只改变观测速度的轻量噪声，既有推理环境版本与专用启动方式保持。

该脚本所有pip install均使用：
env -u PIP_EXTRA_INDEX_URL -u PIP_INDEX_URL PIP_CONFIG_FILE=/dev/null \
  <目标环境python> -m pip install ... --index-url ... --trusted-host ... --no-cache-dir

普通Python依赖走用户指定索引；三种PyTorch cu128发行包还通过
--find-links检索download.pytorch.org的官方cu128目录，避免镜像只有CUDA13默认包。
vLLM使用GitHub官方v0.24.0 tag源码。Git、CMake、可选Rust组件仍可能下载第三方代码；
这不是纯内网离线安装。索引是否具备其余依赖，须远端实际执行确认。

前置检查：Linux、uv、git、GCC/G++>=11.3（本配置限制主版本<=14）、
CUDA Toolkit 12.8的nvcc。nvidia-smi显示12.8只说明驱动能力，并不证明安装了Toolkit。
若Toolkit不在默认位置，可在运行脚本前执行：
export SHORE_CUDA128_HOME='/实际的CUDA12.8目录'
该目录必须包含bin/nvcc；不要把模型目录或GPU驱动目录填在这里。

脚本保留旧.venv-vllm，新建或复用.venv-vllm-cu128；
.venv-trial沿用并安装包内既有requirements-trials.txt，不删除已有环境、源码或结果。
每次源码构建留在build-vllm-cu128.*目录，以便排障。不修改宿主驱动和Conda base。
--plan只检查包目录并打印计划，不安装、不联网、不调用GPU。

安装后使用：
source '<已解压包路径>/.venv-vllm-cu128/bin/activate'
export VLLM_USE_RUST_FRONTEND=0
vllm serve '<实际模型目录>' --host 127.0.0.1 --port 8000 \
  --served-model-name shore-27b --tensor-parallel-size 4 \
  --dtype bfloat16 --max-model-len 32768 --max-num-seqs 1 \
  --gpu-memory-utilization 0.90 --enforce-eager \
  --disable-custom-all-reduce --reasoning-parser qwen3 \
  --limit-mm-per-prompt '{"image":0,"video":0}'

上述启动示例以27B为起点；122B-FP8应替换实际模型路径和服务别名。
不要再调用现有serve_open_models.py或check_4090_environment.py：它们明确锁定0.32/cu129，
会拒绝这个独立配置；这里不自动放宽它们的版本检查。
模型服务仍为localhost:8000/v1，试验客户端的HTTP协议不变。

验证范围：脚本末尾检查pip依赖一致性、每张可见GPU的BF16矩阵计算、
Torch CUDA版本、vLLM两项稳定扩展导入及serve帮助入口。
这些检查不等于完整模型加载、FP8内核、多卡通信、生成或九宇宙测评成功。
交付时只完成本地脚本检查，尚未远端执行安装或加载模型。

官方依据：
https://github.com/vllm-project/vllm/releases/expanded_assets/v0.32.0
https://pytorch.org/get-started/previous-versions/
https://raw.githubusercontent.com/vllm-project/vllm/v0.24.0/requirements/cuda.txt
https://raw.githubusercontent.com/vllm-project/vllm/v0.24.0/requirements/build/cuda.txt
https://raw.githubusercontent.com/vllm-project/vllm/v0.24.0/setup.py
https://recipes.vllm.ai/Qwen/Qwen3.8-27B
