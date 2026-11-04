CUDA 12.8 安装组件（2026-11-04，内部镜像v5）

安装在联网CPU实例完成，之后在有H200的实例运行。实例和镜像保存由用户处理。
CPU安装不要求GPU，也不下载模型、不启动实验、不改宿主驱动。

主项目：/inspire/hdd/project/26-the-other-shore/fengkairui-25026/DiscoverPhysics
资料库：/inspire/hdd/project/26-the-other-shore/fengkairui-25026/test
模型根：/inspire/hdd/project/26-the-other-shore/public/models
环境根：/opt/shore-h200-cu128
工具链：/opt/shore-h200-toolchain
新版外层安装器助手目录：/opt/shore-image-tools-v5

当前默认仅使用传入的Python包索引：
  http://nexus.sii.shaipower.online/repository/pypi/simple
  trusted-host: nexus.sii.shaipower.online
Python包下载不再调用官方Torch下载器，不添加PyTorch/PyPI/FlashInfer官方find-links，
不自动回退PyPI。清除继承的pip索引、find-links和no-index，并禁用继承的pip配置。
明确缺包或下载失败时停止。镜像必须提供当前Python3.12/Linux x86_64适配的精确cu128包；
不得用torch2.11.0默认CUDA版本或其他CUDA构建静默替换torch2.11.0+cu128。

先恢复Conda并激活discoverphy。当前完整入口在主项目：

  SHORE_CONDA_BASE="$(conda info --base)"
  source "$SHORE_CONDA_BASE/etc/profile.d/conda.sh"
  conda activate discoverphy
  PROJECT='/inspire/hdd/project/26-the-other-shore/fengkairui-25026/DiscoverPhysics'
  bash "$PROJECT/scripts/install_all_dependencies.sh" \
    --index-url 'http://nexus.sii.shaipower.online/repository/pypi/simple' \
    --trusted-host 'nexus.sii.shaipower.online'

当前实例已完成工具链、仅需续装时，也可只更新一个入口，无需重新上传项目或手改旧助手：

  SHORE_CONDA_BASE="$(conda info --base)" &&
  source "$SHORE_CONDA_BASE/etc/profile.d/conda.sh" &&
  conda activate discoverphy &&
  PROJECT='/inspire/hdd/project/26-the-other-shore/fengkairui-25026/DiscoverPhysics' &&
  test -d "$PROJECT/scripts" &&
  SHORE_INSTALLER="$(mktemp /tmp/shore-install-v5.XXXXXXXX.sh)" &&
  curl -fL --retry 3 \
    'https://raw.githubusercontent.com/hxh5159/DiscoverPhysics/6e567d306693ea5b64757ceb97b2d3a41f55e83b/scripts/install_all_dependencies.sh' \
    -o "$SHORE_INSTALLER" &&
  printf '%s  %s\n' \
    'eb7db5bc3199e6857ebfa6a6c775073391c16932e1cdd6021feea75f961e7fef' \
    "$SHORE_INSTALLER" | sha256sum -c - &&
  if [ -f "$PROJECT/scripts/install_all_dependencies.sh" ]; then
    cp -p -- "$PROJECT/scripts/install_all_dependencies.sh" \
      "$PROJECT/scripts/install_all_dependencies.sh.$(date +%Y%m%d-%H%M%S).$$.bak"
  fi &&
  install -m 755 -- "$SHORE_INSTALLER" "$PROJECT/scripts/install_all_dependencies.sh" &&
  bash "$PROJECT/scripts/install_all_dependencies.sh" \
    --resume \
    --conda-exe "$SHORE_CONDA_BASE/bin/conda" \
    --mirror-only \
    --index-url 'http://nexus.sii.shaipower.online/repository/pypi/simple' \
    --trusted-host 'nexus.sii.shaipower.online'

SHA校验通过后才备份并更新入口。新入口自动取得v5固定匹配助手，不手工覆盖旧/opt助手目录。
如果是缺少工具链的新实例，只去掉最后安装命令中的--resume；其他参数保持。

首次安装省略--resume；若当前实例已完成工具链阶段，可增加--resume复用工具链。
该入口配置工具链、双Python环境、科学计算依赖、源码vLLM及离线内核准备，逐阶段验收。
仅看到某个包已安装，不代表完整安装已经成功；以最后成功凭据和实际版本检查为准。

本库bootstrap_cuda128.sh与主项目scripts/bootstrap_cuda128.sh相同。
同级四个Python助手须配套保留：pip_index_install.py、prepare_torch_wheel.py、
prepare_vllm_dependencies.py、preflight_cuda128_build.py。
install_cuda128_envs.sh只作兼容委托，将旧--test-root映射为--env-root，
不维护第二套构建逻辑；其余参数原样交给canonical bootstrap。
已有完整CUDA Toolkit12.8（nvcc、ptxas、头文件与真实libcudart）及GCC12时，可单独运行：

  export SHORE_CUDA128_HOME='/opt/shore-h200-toolchain'
  export CC="$SHORE_CUDA128_HOME/bin/x86_64-conda-linux-gnu-gcc"
  export CXX="$SHORE_CUDA128_HOME/bin/x86_64-conda-linux-gnu-g++"
  export PATH="$SHORE_CUDA128_HOME/bin:$HOME/.local/bin:$PATH"
  bash install_cuda128_envs.sh \
    --test-root '/opt/shore-h200-cu128' \
    --cpu-build-for h200 \
    --index-url 'http://nexus.sii.shaipower.online/repository/pypi/simple' \
    --trusted-host 'nexus.sii.shaipower.online'

项目版本保持Python3.12、NumPy2.1.3、SciPy1.15.3、torch2.11.0+cu128、
torchvision0.26.0+cu128、torchaudio2.11.0+cu128、vLLM0.24.0源码、transformers5.8.0。
FlashInfer的cu128离线包也只从传入镜像安装；镜像未收录时明确报错。
Conda工具链、C++/CUDA源码构建的第三方资源，以及非pip离线内核资源不属于pip索引，
仍可能需要公开上游连接；不能把镜像包安装等同于所有网络访问均在内网完成。

仅显式传入--allow-official-fallback才恢复历史官方源兼容路径；当前推荐命令不传该选项。
已有/opt环境、旧助手目录、Torch .part、完整轮子、旧回执、日志与结果均保留。
默认镜像安装不会删除或重新开始旧.part，也不会把未完成下载当作已安装Torch。
已有精确Torch版本复用；新安装的CUDA版本和小型CPU运算仍由bootstrap验证。

构建前继续检查Torch FindCUDA、头文件布局、真实CUDA库及小型CUDA对象编译。
--plan只打印计划，CPU阶段不初始化GPU、不执行kernel、不读取模型。
CPU检查通过不等于H200多卡通信、FP8、FlashInfer运行或真实模型生成已验收。
H200运行使用scripts/serve_model.py与development_worlds.runner；旧0.32/cu129工具仅作历史。

当前模型测试包r12的--refresh保护已有环境、构建目录、wheelhouse/.part、回执和结果。
只git pull不会自动更新已解压包；准备器发现本地源码有修改会停止，避免覆盖。
评分仍80/(1+10e)，80/15/5，每宇宙600秒。真实规律和无噪验证参考与r11原字节一致。
本轮是安装策略/交付检查，尚无真实远端完整安装或GPU/权重运行成功证据。
