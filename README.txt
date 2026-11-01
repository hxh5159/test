SHORE 指挥部私有测试资料库

此仓库包含正式宇宙真实模拟器、定律真值、隐藏验证、指挥部测试工作流。
只限授权指挥部成员，不向攻坚组开放；请保持仓库Private，不将其作为参赛起步包。
没有附带模型权重、真实API key、私钥或本机历史模拟结果。

一、当前使用的四个包（仓库根目录）

shore-organizer-4090-test-20261101.zip
  四张48GB RTX4090，依次测试Qwen3.8-27B和Qwen3.5-122B-A10B-FP8。
  完整步骤见 README_4卡4090双模型测试.txt；当前用户优先采用此包。

shore-organizer-open-model-test-20261101.zip
  四张H200的三模型校准包，27B、122B、397B依次运行。
  完整步骤见 README_三模型远端测试.txt。
  用户后来已有122B-FP8目录，两端需显式指定此目录，优先预量化权重。

shore-organizer-runtime-internal-v5.zip
  正式私有会话、运行与评测系统。不是上述自托管模型校准客户端的替代品。

shore-contest-starter-v2.zip
  公开SDK/参赛模板的当前交付包。与其他私有包分开，不可整库发选手。

packages.json记录每包状态、用途、SHA256和默认解压目录；SHA256SUMS可整体校验。
legacy/保留五个历史交付包供追溯，不用于当前测试。旧闭源校准使用旧10e公式；
runtime-v2/v3为旧评分，v4为旧排名/元数据，starter-v1已由v2替代。
两份before-review/before-clean-test中间草稿不上传，避免误用。

二、远端克隆与4090准备（Linux Bash）

私有仓库需要你自己的GitHub授权或SSH密钥。不要把令牌直接写进URL/命令记录。
以下HTTPS克隆会使用你远端已配置的认证方式；也可用已授权的SSH克隆地址。

  cd /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test &&
  umask 077 &&
  git clone https://github.com/hxh5159/test.git shore-test-assets &&
  cd shore-test-assets &&
  sha256sum -c SHA256SUMS &&
  python3 prepare_test_bundle.py --bundle 4090

最后一步只验证/解压，不调用模型、不运行物理模拟、不加载GPU。
默认解压到仓库目录的同级 shore-organizer-4090-test-20261101，保持前面约定的路径。
此前解压失败留下的空目录可以直接使用。非空未知目录拒绝覆写；用--target指定新目录。
重复准备时校验源文件，保留已有logs/results；源文件被改过则停止，不覆盖你的改动。

确认准备成功后再执行（环境变量必须在当前终端source）：

  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  source "$TESTROOT/env_open_models.sh" &&
  mkdir -p "$SHORE_TEST_ROOT/logs" "$SHORE_TEST_ROOT/results" "$SHORE_TEST_ROOT/checks" &&
  python3 "$SHORE_TEST_ROOT/preflight_open_models.py" \
    --hardware-profile 4090 --models 27b 122b \
    --model-122b /inspire/hdd/global_public/public_models/Qwen/Qwen3.5-122B-A10B-FP8 \
    --json-output "$SHORE_TEST_ROOT/preflight-4090-$(date +%Y%m%d-%H%M%S).json"

任一步报错先停止，勿继续运行依赖其输出的后续命令。
安装建议优先使用仓库根目录的修正版安装入口（uv已经安装后）：

  bash install_4090_envs.sh --test-root "$TESTROOT"

该入口自行恢复并检查路径，空路径不会退化到/.venv-*；复用此前uv缓存，
HTTP读超时600秒、重试5次、同时下载2项，并在任一步失败时停止。
不会删除之前误建的根目录环境，不自动更改驱动、系统CUDA或base环境。
安装成功后做四卡基础BF16计算/扩展导入检查，再下载匹配内核；不启动LLM或科学实验。
使用--plan可仅检查目录并显示目标，不安装、不访问GPU。

用户已实测驱动570.195.03，低于旧说明采用的保守575.57.08门槛。
CUDA12.x小版本兼容可能允许cu129运行，但PTX/JIT/新驱动功能仍需实际验收；
本入口是保留0.32-cu129的受控尝试，不承诺所有vLLM/FP8内核已兼容。
若出现driver/PTX不支持错误，保留日志并换平台兼容节点/环境后继续，不盲降vLLM，
不将cu129 wheel与cu128 Torch混装，也不在GeForce4090上默认安装cuda-compat绕过。
官方规则：https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html
uv下载参数：https://docs.astral.sh/uv/reference/environment/

随后按 README_4卡4090双模型测试.txt，分别在同一计算节点的终端A启动服务、
终端B运行九宇宙校准；基础CUDA通过不等于27B加载/生成或122B-FP8 MoE验收已通过。
已通过clone取得包并由prepare脚本解压后，跳过旧说明的“手动上传/解压”步骤。
H200可用 python3 prepare_test_bundle.py --bundle h200，随后按其说明操作。

三、后续同步

  cd /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-test-assets &&
  git pull --ff-only &&
  sha256sum -c SHA256SUMS

包版本变化时请解压到新目录。已经展开的环境/权重/结果不会因git pull自动更新或覆盖。
不要上传生成的观测日志、凭证、权重和结果，本仓库用于受限同步交付包。

四、测试边界

当前校准仍采用模型提出表达式、工具拟合、隐藏验证评分的内部工作流，
并非模型自动生成任意law.py后通过生产容器的完整验收。
真实定律、数值、配额、80/(1+5e)及80/15/5计分保持当前规则。
已做离线接线和打包检查；是否能在目标GPU上加载、实际速度与成绩仍需远端运行确认。
