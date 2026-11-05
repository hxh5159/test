SHORE 指挥部测试资料库
更新：2026-11-05；当前starter-v12、模型测试包r15、正式运行包strategy-v2。

一、发放范围

shore-contest-starter-v12.zip
  发给攻坚组。根目录README.md说明环境安装、任务、禁止事项、提交与文件边界。包含六公开宇宙、完整可修改agent/、models.json模板、固定SDK/积分器、
  公开评测、格式检查器及说明。五个已提供模型是起步配置，同一个模型可加载多个实例；基础框架默认加载注册表的
  primary_model_id，不会同时加载全部五个。所有本队策略、提示词、工具、记忆和子智能体
  代码均在agent/内；模型权重独立保存，通过models.json按稳定id逐项声明。

shore-organizer-runtime-strategy-v2.zip
  只交指挥部。包含evaluate_strategy.py、九隐藏真实环境、验证真值及固定评分程序。
  指挥部在自己的目录保管环境，以管理员权限接收agent目录与models.json两条路径，
  通过统一命令启动队伍策略。策略以指定普通评测账号运行，官方SDK可读，真实环境与
  运行材料留在管理员私有目录；不能把管理员本人的权限继承给队伍程序。
  当前正式仅测Adam、Ramiel、Leliel，九宇宙定义及参考全部保留，权重0.3/0.4/0.3。
  public/包含同一完整开发包，供指挥部的固定SDK、积分器及接口使用。

shore-organizer-open-model-test-20261101.zip（r15，4H200）
shore-organizer-4090-test-20261101.zip（r15，4×48GB4090诊断）
  组合公开开发组件及指挥部运行系统，仅供指挥部内部测试，不整体发送攻坚组。
  六公开开发入口与正式评测使用同一agent目录、模型注册表和实验/交卷协议。
  不附带模型张量、API密钥、任务数据库或历史运行材料。

本test仓库按所有者明确授权保持public。仓库访问权限与比赛发放受众分别管理；向攻坚组
只发独立starter，不能将包含真实模拟器的整个仓库或完整模型测试包作为开发包交付。

二、同步与准备（远端Linux）

BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
ASSETROOT="$BASE/test"
RUNTIME="$BASE/shore-organizer-runtime-strategy-v2"

git -C "$ASSETROOT" pull --ff-only
python3 "$ASSETROOT/prepare_test_bundle.py" --bundle runtime --target "$RUNTIME"

如目标已由旧receipt管理，需要更新，使用同一命令加--refresh。准备器检查全部SHA，
保护已有环境、缓存、日志和结果；人工改动的受管理源文件会停止刷新。starter/h200/4090
也有同名bundle键，分别选用各自目标目录。新实验始终使用新的结果目录。

三、统一策略与模型路径

攻坚组交两条绝对路径：
  /path/to/team01/agent
  /path/to/team01/models.json

agent/内含run.py、__init__.py、strategy.json及本队全部辅助代码。strategy.json记录队伍、
提交和版本身份。models.json为每个实际使用的模型声明唯一id、白名单base_model、完整
checkpoint路径、可选adapter_path及用途role，并指定primary_model_id。相同底座的不同
训练检查点使用不同id，全部列入清单。公共底座可引用公共模型目录，不要求重复复制大模型权重。

指挥部统一设置评测账号与解释器，为该普通账号授予策略目录、模型目录及父目录的必要
读取/遍历权限。测评期间本次策略、配置及所有声明权重保持可读且不被改写。管理员能
读取某路径不等于评测账号也能读取；先执行check-only核对。具体命令及账号设置见
README_策略路径测评.txt。六公开操作见开发包docs/STRATEGY_SUBMISSION.txt和QUICKSTART.txt。

模型权重根默认：/inspire/hdd/project/26-the-other-shore/public/models。
主项目：$BASE/DiscoverPhysics；测试资料库：$BASE/test。模型推理解释器与实验解释器由
实际配置决定；CPU联网安装与无网H200运行的环境步骤见主项目docs/H200_OFFLINE_SETUP.txt。
本轮文件组织调整不代表已在远端加载真实模型，旧CUDA安装说明按相应实际环境核对。

四、测评及反馈

六公开开发仍覆盖1—6号，开发及测评固定每界3次模型决策，不得修改或绕过；正式运行默认选择三个隐藏
宇宙，每界600秒，自首次mission开始，模型加载另计。单界评分80/(1+10e)、80/15/5，
能量100、observe20及无噪评分真值规则保持。三个宇宙一次完整运行汇总后才反馈成绩，
只反馈总分与各宇宙总分；隐藏观测、对话、候选、日志、新记忆和更新权重由指挥部保留。

五、清单与历史

packages.json给出当前包、历史包、版本、用途和SHA，SHA256SUMS可用sha256sum -c核验。
远端建议目录见远端文件结构.txt。两份逐文件清单及交付说明见参赛者开发包_文件清单.txt、指挥部测评包_文件清单.txt、
交付说明.txt；每个ZIP自带FILE_LIST和内容摘要。legacy保留旧starter-v10/runtime-r3/r13
及更早原始文件，不重新生成历史验证真值。旧直接项目入口与表达式校准仅保留兼容。
