历史兼容资料（2026-11-05）：当前正式流程以README_策略路径测评.txt为准。指挥部在自己的私有目录保管真实环境，接收agent目录与models.json两条路径，并通过专用普通评测账号运行策略。下文旧直接项目或容器流程保留供历史核对，正式环境无需放进参赛者项目。

2026-11-05当前运行约定：六公开全部保留，基础框架每宇宙默认最多3次模型决策；正式入口使用direct-v1-r3，仅运行Adam、Ramiel、Leliel，原九宇宙定义与无噪验证数据全保留。正式操作见README_直接项目测评.txt。下文表达式校准为历史诊断入口，不替代当前law.py基础框架。

SHORE 指挥部模型与完整law.py流程（2026-11-04，r12）

当前正式方式：单实例中直接运行队伍当前项目，测评期间停止编辑；不要求容器封装。
六公开入口保持development_worlds.runner；九正式外接后使用scripts/evaluate_submission.py。
完整当前命令见同包README_直接项目测评.txt，direct-v1-r2正式配置沿用原九界干净参考。
当前包的Python包默认仅从指定镜像安装，精确cu128缺包即停止，不自动切换官方源；仅显式--allow-official-fallback恢复兼容路径。
CUDA源码构建和离线内核资源可能需要公开上游连接；不表示远端安装或GPU已实测通过。
下文旧镜像/容器受理说明仅为历史兼容；真实权重/H200验收与协议联调分别记录。

一、当前内容与边界

本目录包含最新九宇宙指挥部运行程序与验证参考，同时包含完整公开六环境和可修改LLM
基础框架。这里只供指挥部测试，不作为整个参赛发放包。给攻坚组的仅starter-v9，或本目录
中经公开白名单打包的部分；不能把本目录中的真实九宇宙程序、配置或参考送进队伍镜像。
本轮只更新安装组件与相关指引，保持固定参数、600秒、现行噪声和80/(1+10e)计分；旧r11及其结果保留历史。

二、环境与模型

source env_open_models.sh
PY='/opt/shore-h200-cu128/.venv-trial/bin/python'
MPY='/opt/shore-h200-cu128/.venv-vllm-cu128/bin/python'
MODELROOT='/inspire/hdd/project/26-the-other-shore/public/models'

先在联网CPU完成CUDA12.8镜像和离线内核准备，再在无网H200执行真实加载。
完整说明见docs/H200_OFFLINE_SETUP.txt。当前统一入口scripts/serve_model.py和shore_agent，
不调用旧0.32/cu129专用启动器，也不将旧JSON表达式校准当正式law.py基线。

三、先检查六公开完整运行

"$PY" scripts/serve_model.py --list
"$PY" -m development_worlds.runner --worlds 1 2 3 4 5 6   --model 27b --model-root "$MODELROOT" --model-python "$MPY"   --output "results/public-$(date +%Y%m%d-%H%M%S)"

可选择27b、35b、35b-fp8、122b、122b-fp8、397b、397b-fp8。
BF16/FP8不互相冒充；397b纯BF16不能在4H200全GPU常驻，通常选397b-fp8。
六公开开发的记录可复用，同一agent还可交指挥部九隐藏驱动，不改探索程序。

四、九隐藏完整测试及正式部署

profiles/internal-v9/profile.json包含最新九界固定科学定义和验证；正式配置、模型只读挂载、
两类镜像和真实H200生成验收按README_正式赛题部署.txt及CODE_DELIVERY_BOUNDARIES.txt。
新configure_runtime.py提供configure/preflight/model-smoke/release-reviewed四个可执行步骤。
不要虚构镜像sha256或仅翻发布flag；现场命令会取得本机实际镜像/设备/真实生成证据。
九隐藏只反馈总分/各宇宙总分和必要启动格式错误，观测、对话、日志、候选和更新权重
均由指挥部保留；旧export-team功能已拒绝，不使用旧归还规则。

五、历史工具

open_model_calibration.py、closed_expression_trial.py等为组委会旧诊断流程，保留以兼容
历史数据及源码追溯。serve_open_models.py/check_open_model_service.py仍是旧版本辅助，
当前默认流程不依赖它们。新工作流直接产law.py，走同一固定积分/评分，不需要先提交
JSON数学表达式。模型能力和成绩要以真实权重在目标设备的新运行记录判断。

硬件建议：4H200：优先27b、122b-fp8、397b-fp8。
