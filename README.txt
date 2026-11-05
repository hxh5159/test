SHORE 指挥部测试资料库
更新：2026-11-05；当前starter-v10、模型测试包r13、正式运行包direct-v1-r3。

一、四个包的用途

shore-contest-starter-v10.zip
  发给攻坚组的完整开发包：六公开宇宙、可修改LLM基础框架、统一实验/提交驱动、
  固定候选积分器、公开评分、七模型配置、统一正式入口、最新8页说明PDF及CUDA12.8指引。
  基础智能体默认每宇宙最多3轮模型交互；不含九隐藏真实场、真值或真实模型权重，见包内FILE_LIST.txt。

shore-organizer-runtime-direct-v1-r3.zip
  指挥部九隐藏运行系统，沿用最新固定科学定义、覆盖和原字节干净参考，不改物理或计分。
  public/是同一完整攻坚组开发包；整个runtime ZIP不能作为参赛包发放。
  保留全部九界配置和无噪参考，当前仅运行Adam、Ramiel、Leliel，档位权重仍为0.3/0.4/0.3。
  直接运行队伍当前项目，九界环境外接，无需Docker、项目复制或模型挂载映射。
  固定配置direct-v1-r3；当前命令见README_直接项目测评.txt，完整清单见包内FILE_LIST.txt。

shore-organizer-open-model-test-20261101.zip（r13，4H200）
shore-organizer-4090-test-20261101.zip（r13，4×48GB4090开发诊断）
  将完整公开开发包与指挥部运行源/新参考合在同一测试目录，兼容此前解压位置。
  主入口为scripts/serve_model.py和python -m development_worlds.runner，正式测评用
  scripts/evaluate_submission.py --organizer-root .。旧容器与表达式校准入口仅兼容保留。
  两个包含九隐藏真实资料，只用于指挥部；不要把整个目录发给攻坚组。六公开开发仍覆盖1—6号，
  基础框架开发和正式测评均默认3轮，默认正式测评只运行上述3界，其余6界完整保留。

2026-11-02所有者已明确授权公开整个hxh5159/test，含模拟器、真值和验证；匿名HTTPS
读取不要求GitHub登录。访问权限与正式参赛发放受众分开：只把独立starter发给攻坚组。
不附API凭证、私钥、权重或原始模型运行结果。历史标识保留原字节，不代表重新改变仓库权限。

二、远端准备（Linux，已有test克隆）

BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
ASSETROOT="$BASE/test"
TESTROOT="$BASE/shore-organizer-open-model-test-20261101"
git -C "$ASSETROOT" pull --ff-only

首次解压：
python3 "$ASSETROOT/prepare_test_bundle.py" --bundle h200 --target "$TESTROOT"

已有旧包receipt、需要更新源码：
python3 "$ASSETROOT/prepare_test_bundle.py" --bundle h200 --target "$TESTROOT" --refresh

只执行适用的一条。4090诊断将bundle换为4090并使用原4090目标目录；runtime/starter也有
对应bundle键。准备器校验全部哈希，更新receipt管理的源文件，保护环境、缓存、日志及结果。
源文件若被人工改动会停止，不自动覆盖。新实验使用新的输出目录，不伪改旧成绩。

三、当前环境和完整模型流程

用户实际在联网CPU安装/编译并保存镜像，再到无网H200运行，目标CUDA12.8。
安装步骤见主项目docs/H200_OFFLINE_SETUP.txt；安装不用读取本仓库，更不要求GPU在CPU端出现。
当前包也带这些公开安装脚本和说明。旧0.32/cu129安装/检查工具仅作兼容保留，不是当前入口。

source "$TESTROOT/env_open_models.sh"
cd "$TESTROOT"
PY='/opt/shore-h200-cu128/.venv-trial/bin/python'
MPY='/opt/shore-h200-cu128/.venv-vllm-cu128/bin/python'
MODELROOT='/inspire/hdd/project/26-the-other-shore/public/models'

"$PY" scripts/serve_model.py --list
"$PY" -m development_worlds.runner --worlds 1 2 3 4 5 6   --model 27b --model-root "$MODELROOT" --model-python "$MPY"   --output "results/public-$(date +%Y%m%d-%H%M%S)"

七个预设：27b、35b、35b-fp8、122b、122b-fp8、397b、397b-fp8。
BF16与FP8不会互相冒充；397b BF16无法4H200全GPU常驻，应选现有FP8或另行验证合规方案。
六公开可直接保留实验资料；九隐藏赛中不归还观测、对话、候选、日志、记忆或更新权重。
正式分数仍80/(1+10e)、80/15/5；600秒从首次mission起计，模型加载另计。

六公开完整命令：解压目录docs/QUICKSTART.txt、PARTICIPANT_FILES.txt、MODEL_RUNTIME.txt。
九隐藏直接项目测评：README_直接项目测评.txt、CODE_DELIVERY_BOUNDARIES.txt。
指挥部接入九界后，从队伍当前项目运行scripts/evaluate_submission.py，测评期间禁止
编辑代码、配置和改写本次权重。指挥部不覆盖队伍入口、策略或模型配置。

四、校验与历史

packages.json记录每包版本、用途、SHA及默认解压目录；SHA256SUMS包含当前和全部历史包。
可用sha256sum -c SHA256SUMS核对。legacy/保留旧v3/r6/v9及更早原始包和评分版本。
当前安装组件v5默认仅使用指定内部镜像安装Python包，不再调用官方Torch下载器、
官方find-links或自动回退PyPI。镜像缺少精确cu128版本时明确停止；仅显式--allow-official-fallback恢复旧行为。
C++/CUDA源码及离线内核资源不属于pip索引，仍可能访问公开上游。匹配助手随包提供。
当前正式profile为direct-v1-r3，只选择3界运行；宇宙规律、无噪验证、600秒、配额和单界计分保持。
原starter-v9/r12/direct-v1-r2及更早版本留存legacy原字节，不重生成验证真值。
根目录可能留有旧版本原件，当前入口始终以packages.json的current记录为准。
最新发布与现场GPU验收是不同步骤：本地回归及合成HTTP联调不代表所有真实模型均已加载。
