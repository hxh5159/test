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

shore-organizer-runtime-internal-v6.zip
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
  git clone https://github.com/hxh5159/test.git test &&
  cd test &&
  sha256sum -c SHA256SUMS &&
  python3 prepare_test_bundle.py --bundle 4090

最后一步只验证/解压，不调用模型、不运行物理模拟、不加载GPU。
此段只用于首次克隆；你已有的实际仓库为.../test/test，后续用第三节同步，不重复clone。
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

  ASSETROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/test'
  TESTROOT='/inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/shore-organizer-4090-test-20261101'
  bash "$ASSETROOT/install_4090_envs.sh" --test-root "$TESTROOT"

该入口自行恢复并检查路径，空路径不会退化到/.venv-*；复用此前uv缓存，
HTTP读超时600秒、重试5次、同时下载2项，并在任一步失败时停止。
不会删除之前误建的根目录环境，不自动更改驱动、系统CUDA或base环境。
如果之前失败的下载在默认uv缓存，可在上条命令中增加
--cache-dir "$(env -u UV_CACHE_DIR uv cache dir)"；这避免已source环境后改换缓存目录而重复下载。
安装成功后做四卡基础BF16计算/扩展导入检查，再下载匹配内核；不启动LLM或科学实验。
vLLM0.32 CUDA扩展检查使用_C_stable_libtorch和_moe_C_stable_libtorch，不使用旧_C名称。
使用--plan可仅检查目录并显示目标，不安装、不访问GPU。

本次复查后，完整的分阶段检查可执行：

  python3 "$ASSETROOT/check_4090_environment.py" --phase paths --test-root "$TESTROOT" &&
  bash "$ASSETROOT/install_4090_envs.sh" --test-root "$TESTROOT" &&
  python3 "$ASSETROOT/check_4090_environment.py" --phase installed --test-root "$TESTROOT"

paths阶段检查包内源码清单/语法、模型头部、目录读写；installed阶段使用两个明确的venv
检查CPU依赖/CLI、0.32-cu129扩展、四卡显存与小BF16计算，生成新的JSON报告。
只有ready_for_model_service_checks才继续模型服务验收；它不等于模型已加载或已跑九宇宙。
驱动/网络/模型行为仍需当前节点实际验收。源码改动后先执行第三节的--refresh，保留环境和结果。

当前校准工具1.1修复合法thinking-only/length回复被误报transport的问题，仍保持原thinking与
8192/32K/900设置；跨截止的context错误也保留原故障类型，不伪装成模型科学零分。

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

  cd /inspire/hdd/project/urbanlowaltitude/fengkairui-25026/houwenzhe/test/test &&
  git pull --ff-only &&
  sha256sum -c SHA256SUMS &&
  python3 prepare_test_bundle.py --bundle 4090 --refresh

--refresh只更新仍等于原交付内容的源码；已改动的文件会拒绝覆盖，环境/权重/结果不重建。
若提示存在本地源码改动或包删除了旧文件，请保留原目录并用--target选择新目录。
不要上传生成的观测日志、凭证、权重和结果，本仓库用于受限同步交付包。

四、测试边界

当前校准仍采用模型提出表达式、工具拟合、隐藏验证评分的内部工作流，
并非模型自动生成任意law.py后通过生产容器的完整验收。
当前计分统一为80/(1+10e)，评分版本draft-3.11.0；真实定律、数值、配额、80/15/5和P>=40节约资格不变。旧5e结果不自动改写为新成绩，重测请使用新的结果目录。
已做离线接线和打包检查；是否能在目标GPU上加载、实际速度与成绩仍需远端运行确认。
