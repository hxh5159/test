指挥部：单实例直接项目测评（2026-11-05）

一、当前方式

直接运行攻坚组当前项目目录及已配置模型，不要求封装镜像、复制项目或容器模型映射。
窗口开始后禁止攻坚组编辑代码、配置及改写本次所用权重，并确认检查点已经写完。
推理服务若在更新权重前已启动，应确认重新加载本次模型。实例/镜像保存、复制和上传
由负责人处理，不属于测评步骤。接入环境不会覆盖队伍自己的策略、代码或模型配置。

六公开宇宙用于开发自测，源码和评测公开；九正式宇宙由指挥部接入。队伍智能体仍在
所选Adam、Ramiel、Leliel三界自动实验、拟合、交law.py与claims.json，再由指挥部固定积分、比较无噪真值评分。

二、默认路径和依赖

  BASE='/inspire/hdd/project/26-the-other-shore/fengkairui-25026'
  PROJECT="$BASE/DiscoverPhysics"
  PY='/opt/shore-h200-cu128/.venv-trial/bin/python'
  RUNTIME="$BASE/shore-organizer-runtime-direct-v1-r3"

测试资料库为$BASE/test。公共模型根为：
  /inspire/hdd/project/26-the-other-shore/public/models
推理解释器默认为/opt/shore-h200-cu128/.venv-vllm-cu128/bin/python。
可按该队实际环境修改解释器；模型、额外依赖均应提前就绪，测评时不联网安装/下载。

三、接入九宇宙

当前包shore-organizer-runtime-direct-v1-r3.zip含九界真实模拟器、无噪参考、直接执行
启动器和固定评分，并附匹配public/。此包由指挥部接入，不是参赛开发包；starter-v10
不含九界真实规律和隐藏真值。指挥部管理运行包及隐藏材料，按既定安排清理环境并
留存审计资料。进程分离及目录名本身不保证文件系统隔离。

如已在远端同步test仓库：
  "$PY" "$BASE/test/prepare_test_bundle.py" --bundle runtime --target "$RUNTIME"

四、窗口前统一入口自检

队伍保留submission.json，entrypoint为其实际程序参数数组，models填写白名单底座、
实际宿主路径或项目内相对训练成果路径；无需/models挂载。LoRA由队伍入口加载底座
和对应适配器。指挥部不要重新生成/覆盖该队已有清单、提示词、配置或智能体模块。
先在六公开宇宙验证同一入口，再由指挥部接入环境后检查启动条件：

  "$PY" "$PROJECT/scripts/evaluate_submission.py" \
    --organizer-root "$RUNTIME" --project-root "$PROJECT" \
    --manifest submission.json --output "$BASE/shore-results/window1-team01" \
    --agent-python "$PY" --check-only

check-only不加载模型、不运行物理或生成正式成绩，不等同于实际模型生成验收。

五、正式统一命令

  "$PY" "$PROJECT/scripts/evaluate_submission.py" \
    --organizer-root "$RUNTIME" --project-root "$PROJECT" \
    --manifest submission.json --output "$BASE/shore-results/window1-team01" \
    --agent-python "$PY"

换队/窗口仅调整项目目录、实际解释器和本次全新输出目录。不得覆盖已有结果。
四窗口/四次机会由指挥部手工受理控制，不给队伍程序增加复杂计数系统。

六、规则和结果

每界首次成功mission起600秒，模型加载另计，探索结束后的固定积分评分另计。
基础框架每界默认3次模型决策，最后一轮优先交卷。100能量、20次observe；物理采样严格对齐0.005；第一束光2探针各8时刻。
预言80/(1+10e)，三条声明各5分，预言>=40才计5分节约；档位权重0.3/0.4/0.3，总分=0.3×Adam+0.4×Ramiel+0.3×Leliel；其余六界不运行也不计零。
取最高一次完整三界成绩，不拼接逐宇宙历史最高分；同分按同次加权节约分升序。

summary.json与终端仅给总分、所选三界总分及必要启动/格式错误；不反馈分项、声明正误、
验证误差或真值轨迹。观测、对话、日志、候选、新记忆/权重和详细评分在output/private
下，由指挥部赛中留存、不归还队伍；实际目录权限按现场规则管理。
超时用最后及时有效配对；无有效配对该界0分；指挥部基础设施故障不计为科学零分，
不发布部分三界总分，修复后依规则重评。

七、正式配置和证据

direct-v1-r3保留全部九界配置和已收敛无噪参考，仅选择Adam、Ramiel、Leliel参与本次测评，
不改变力律、验证轨迹或计分。启动解释器保留venv路径，不解析到其系统Python目标。
启动护栏900秒、单次候选推演120秒、关闭30秒，均不同于探索600秒。
配置核验固定SDK、私有科学/评分源码与参考摘要；不依赖Docker发布回执。
配置正式发布不代表已在H200加载真实模型。协议端到端、数值检查、真实权重/多卡
部署分别报告；合成模型服务或协议测试agent只证明工程流程，不代表LLM发现能力。
旧contest_platform容器和local-diagnostic方式仅兼容保留，不伪造镜像ID或翻标签评分。
