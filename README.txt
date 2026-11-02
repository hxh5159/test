SHORE 指挥部测试资料库
更新：2026-11-02；当前starter-v4、模型测试包r7、正式运行包internal-v9-r2。

一、四个包的用途

shore-contest-starter-v4.zip
  发给攻坚组的完整开发包：六公开宇宙、可修改LLM基础框架、统一实验/提交驱动、
  固定候选积分器、公开评分、七模型配置及CUDA12.8环境/运行说明。不含九隐藏真实场或真值。

shore-organizer-runtime-internal-v9-r2.zip
  指挥部九隐藏运行系统，已迁入最新固定科学定义与增强验证覆盖，九套干净参考重新生成。
  public/是同一完整攻坚组开发包；整个runtime ZIP不能作为参赛包发放。
  configure_runtime.py可登记真实镜像/模型挂载，执行目标设备检查、真实模型生成和受信发布。

shore-organizer-open-model-test-20261101.zip（r7，4H200）
shore-organizer-4090-test-20261101.zip（r7，4×48GB4090开发诊断）
  将完整公开开发包与指挥部运行源/新参考合在同一测试目录，兼容此前解压位置。
  主入口改为scripts/serve_model.py和python -m development_worlds.runner，正式九界用
  contest_platform.py。旧表达式校准辅助仍留作历史诊断，不作为新law.py基础框架入口。
  两个包含九隐藏真实资料，只用于指挥部；不要把整个目录发给攻坚组。

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
九隐藏隔离部署：README_正式赛题部署.txt、CODE_DELIVERY_BOUNDARIES.txt。
正式镜像ID从实际本地构建取得；模型源目录由指挥部只读映射，不需要反复上传数百GB基座。

四、校验与历史

packages.json记录每包版本、用途、SHA及默认解压目录；SHA256SUMS包含当前和全部历史包。
可用sha256sum -c SHA256SUMS核对。legacy/保留旧v3/r6/v9及更早原始包和评分版本。
此次r7/v9-r2仅更新项目路径与资料指引，仍使用internal-v9科学profile；starter-v4原字节保持。
最新发布与现场GPU验收是不同步骤：本地回归及合成HTTP联调不代表所有真实模型均已加载。
