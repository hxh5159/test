CUDA 12.8 安装组件（2026-11-03）

安装在联网CPU实例完成，之后在有H200的实例运行。实例和镜像保存由用户处理。
本次安装不要求CPU实例有GPU，也不下载模型、不启动实验、不改宿主驱动。

主项目：/inspire/hdd/project/26-the-other-shore/fengkairui-25026/DiscoverPhysics
资料库：/inspire/hdd/project/26-the-other-shore/fengkairui-25026/test
模型根：/inspire/hdd/project/26-the-other-shore/public/models
环境根：/opt/shore-h200-cu128

本库根目录中的bootstrap_cuda128.sh与主项目scripts/bootstrap_cuda128.sh相同。
同级三个Python助手须配套保留：pip_index_install.py、
prepare_vllm_dependencies.py、preflight_cuda128_build.py。
install_cuda128_envs.sh仅作兼容委托，将旧--test-root映射为--env-root，
不维护第二套构建逻辑；其余参数原样交给上述bootstrap。

安装所需完整CUDA Toolkit12.8须已存在（包括nvcc、ptxas、头文件和真实libcudart）；
若尚无工具链，按主项目scripts/install_all_dependencies.sh的完整入口安装。
该外层入口在主项目提供，不放入参赛者ZIP。不要只复制bootstrap一个文件。
完整部署说明见主项目docs/H200_OFFLINE_SETUP.txt和docs/CUDA128_SETUP.txt。

已有工具链时，从本资料库运行的示例：

export SHORE_CUDA128_HOME='/opt/shore-h200-toolchain'
export CC="$SHORE_CUDA128_HOME/bin/x86_64-conda-linux-gnu-gcc"
export CXX="$SHORE_CUDA128_HOME/bin/x86_64-conda-linux-gnu-g++"
export PATH="$SHORE_CUDA128_HOME/bin:$HOME/.local/bin:$PATH"
bash install_cuda128_envs.sh \
  --test-root '/opt/shore-h200-cu128' \
  --cpu-build-for h200 \
  --index-url 'http://nexus.sii.shaipower.online/repository/pypi/simple' \
  --trusted-host 'nexus.sii.shaipower.online'

目标：Python3.12、实验NumPy/SciPy/pytest、torch2.11.0+cu128、
torchvision0.26.0+cu128、torchaudio2.11.0+cu128、vLLM0.24.0源码、transformers5.8.0。
它保留已有日志、结果、缓存和非目标环境；失败阶段有独立日志，不把部分完成当作成功。

pip使用用户指定格式，清除PIP_INDEX_URL/PIP_EXTRA_INDEX_URL并禁用继承的pip配置。
指定镜像下载404或连接失败时，仅单次切换官方PyPI重新解析，不混合多个索引。
构建前检查Torch FindCUDA、真实CUDA库、头文件布局和小型CUDA对象编译；
随后预下载并核验缺失的Python依赖。C++/CUDA源码构建仍可能下载公开第三方资源，
联网CPU阶段须允许这些连接；不保证只访问内网镜像。

安装器可用--plan只打印计划；CPU端不初始化GPU，不运行kernel或读取模型。
CPU编译完成不等于H200的FlashInfer内核、多卡通信、FP8、真实生成或科学测评成功。
H200上使用项目当前scripts/serve_model.py与development_worlds.runner；
不要再使用锁定旧0.32/cu129的serve_open_models.py或check_4090_environment.py。

r9模型测试包的--refresh保护旧.venv*、构建目录、日志、缓存和结果；
只git pull不会自动更新已解压包。源文件有本地修改时准备器会停止，避免覆盖。
计分仍80/(1+10e)，80/15/5，每宇宙600秒。宇宙参数、验证真值与旧r8相同。
本次包和安装组件完成本地结构/回归检查，不声称用户远端已经安装或加载模型成功。
