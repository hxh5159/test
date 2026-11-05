# 测试资料库协作约定

最后更新：2026-11-05（北京时间）。

当前交付（2026-11-05）：starter-v12、runtime-strategy-v2、模型测试包r15，实际文件数为90/161/196/197，见packages.json及FILE_LIST。
本轮开发包根目录新增README.md，避免SDK/SHA等无关术语，包含任务、依赖、运行、文件边界和提交。
现行只保留27B/35B/122B三个Qwen家族、五个提供目录，不含397B；执行白名单、机器声明和赛题说明同步。
同一模型可加载多个实例，同源权重可复用清单ID及路径，不同训练结果/适配器分别声明。
按用户要求删除当前说明中非白名单/API生成数据蒸馏的特定禁令，不额外宣告允许；其他推理/框架/运行禁网限制保持。
远端选手和指挥部结构见远端文件结构.txt。旧starter-v11/runtime-strategy-v1/r14原字节归档，科学与参考不改。
全部可修改策略统一在agent/目录内，固定入口agent/run.py；策略目录含strategy.json及本队全部
提示词、工具、记忆配置和多智能体协调代码。models.json逐项声明全部实际底座/完整训练权重
及可选LoRA路径，使用唯一id区分同底座不同检查点并指定primary_model_id。
用户已明确指挥部拥有管理员权限，通过agent目录与models.json两条路径读取各队方案；
真实环境只在指挥部目录，不再要求接入参赛者项目。指挥部固定入口evaluate_strategy.py
以管理员启动、指定独立普通评测账号运行策略，账号权限、环境可见性与模型路径预检由新运行器检查。
主入口与标准SDK独立保管，所有队伍策略以路径引用，权重不随ZIP复制或上传。公共底座可复用。
当前正式仍只测Adam、Ramiel、Leliel，每档一个，权重0.3/0.4/0.3；九宇宙全部定义和无噪参考
及六公开开发环境保留。基础框架默认每界3轮，600秒、100能量/20观测、80/(1+10e)及80/15/5保持。
隐藏运行材料由指挥部留存，赛中只反馈总分与所测各宇宙总分。旧直接项目与表达式校准仅兼容。
发放只使用starter-v12；runtime与完整模型测试包只交指挥部；本test仓库按用户既有授权保持public。
保留旧starter-v10/runtime-r3/r13及更早包原字节，现有环境/缓存/结果通过显式--refresh保护。
新profile、受众边界、四类旧包刷新、归档校验与逐文件清单均已通过。本轮包为90/161/196/197文件，
106项科学/旧配置/参考保持原字节、56归档校验通过，资料库36项检查含受限权限分项复核通过。
真实GPU/权重加载和普通账号权限现场验收单独记录，不把脚本化服务或元数据检查冒充模型加载。

上一版安装恢复验收：内网包索引存在但档案404导致pip中断，和此前FindCUDA报错分开记录。
同步主库匹配bootstrap及三个助手，旧--test-root入口只作委托；核心版本/cu128不放宽。
新包实际九界端到端及固定积分评分已在脚本化本机模型服务中通过，不表示真实模型/GPU验收。
公开224、正式执行相关42、资料库36项回归通过，平台跳过分别4/3/0；32份ZIP校验及r8刷新保护通过。
所有真实物理/参考和规则保持。完整安装器固定提交b185d07ee0d2a805dee439434e4cbe4de6861908，
匿名实际下载外层及六匹配组件的原字节SHA均通过；尚无用户远端新版安装成功证据。

2026-11-03历史安装补丁：Triton3.6.0内网下载RemoteDisconnected，新版pip多行消息使旧
备用源分类器漏识别，现已修复并同步匹配组件。完整安装器版本multiline-download-v3，
助手默认/opt/shore-image-tools-v3；新实例先激活discoverphy，不默认已有旧/opt环境。
本轮科学profile direct-v1-r2和全部科学/执行payload原字节保持，只做安装、ZIP、CLI及
r9刷新保护验收，不重新跑模型/科学端到端；旧包实际九界证据和原摘要在legacy保留。
本轮资料库36项回归通过、36份登记归档SHA及CRC通过；当前四包的每个非安装/文档/
清单payload与r9原字节一致，科学profile及无噪参考保持，未执行真实远端安装。

2026-11-04安装补丁：固定Torch轮子先持久化下载、续传及SHA核验，本地完整轮子复用；
同步CMake预检初始化修正。完整安装器使用/opt/shore-image-tools-v4，旧脚本和环境保留。
root bootstrap与四个Python助手配套，install_cuda128_envs.sh保持--test-root兼容委托。
科学profile仍direct-v1-r2，不改变真实场、参考、评分、配额、600秒或提交协议；仅做安装/
归档/CLI/安全刷新检查，不重跑模型/科学端到端，旧包端到端证据按原摘要留存legacy。
本轮资料库36项回归、40份登记归档SHA及CRC、全部四类包的r10→r11显式刷新保护通过；
刷新核对保留wheelhouse中的.part和旧回执fixture，包内排除下载轮子/临时锁/缓存/权重。
124项固定SDK/科学源码/profile/无噪参考/PDF保持，非安装与相关文档/打包元数据payload原字节不变。

2026-11-04当前安装策略：用户明确要求Torch及vLLM等Python依赖使用指定内部镜像。
当前默认mirror-only：不调用官方Torch下载器，不添加官方find-links，不自动回退PyPI；
保留torch2.11.0+cu128、torchvision0.26.0+cu128、torchaudio2.11.0+cu128、vLLM0.24.0源码和
Transformers5.8.0的精确约束。镜像缺少适配包时明确停止，不切换CUDA或版本。
仅显式--allow-official-fallback恢复历史下载路径；旧v4组件/原.part/环境及日志保留，
新助手目录为/opt/shore-image-tools-v5。Conda工具链、CMake第三方源码和额外离线内核资源
不属于pip索引，仍可能访问公开上游。此次只更新安装组件、指引和归档，科学/执行代码、
profile、无噪参考、固定参数、计分及600秒不改，不表示真实远端安装或GPU/模型运行通过。
本次44份登记归档SHA/CRC、四类r11→r12安全刷新和资料库36项回归均通过；124项SDK/科学/参考/PDF保护核验保持。
匹配助手固定提交31754aa5e1b7ffb39388c6a3c46d28e0c3624609，内部镜像是否收录所需cu128包仍须在远端实际确认。

1. 用户已长期授权：本仓库有修改时，完成相应检查后自动执行Git commit并推送至origin，不再等待额外提醒或重复确认。无改动不创建空提交；用户后续明确要求暂停推送或仅本地保存时优先遵守。
2. 本仓库为`hxh5159/test`。2026-11-02用户在明确知晓内容后确认公开整个仓库，包括正式宇宙真实模拟器、定律真值和隐藏验证；已核实visibility=public。此确认覆盖此前本仓库必须private的约定，不得自动改回private。仓库公开不等于所有内容都是正式参赛发放包，发放边界仍按各包用途区分。
3. 与项目仓库`hxh5159/DiscoverPhysics`分别管理。不上传API凭证、私钥、模型权重或未经明确需要的原始运行结果；本仓库公开不扩大上述授权，也不自动公开仓外记忆。推送前核对范围和目标仓库。
4. 当前有效包在根目录，旧交付版本在`legacy/`；遵守`packages.json`中的用途/状态及`SHA256SUMS`。更换压缩包时同步校验清单；不要让历史评分配置成为当前默认入口。
5. 实际运行位置为远端Linux。2026-11-02用户更新长期默认：主库`/inspire/hdd/project/26-the-other-shore/fengkairui-25026/DiscoverPhysics`，本测试库`/inspire/hdd/project/26-the-other-shore/fengkairui-25026/test`；H200/4090解压目标分别为其上级目录中的`shore-organizer-open-model-test-20261101`/`shore-organizer-4090-test-20261101`。模型根仍为`/inspire/hdd/project/26-the-other-shore/public/models`，镜像内`/opt/shore-*`环境不变。旧项目路径仅作历史，后续命令默认使用新路径。
6. 提供的命令须自行恢复并验证路径，依赖步骤失败时停止，避免空变量派生根目录路径；保护用户已有环境、源码、观测和结果，不自动删除未知目录。
7. 离线检查、解压校验、基础CUDA检查与完整模型/科学评测分别记录。未真实加载模型或取得用户执行证据时，不声称远端已经运行成功。
8. 每次同步完成后核对远端分支与本地提交一致，并报告真实SHA与推送状态；不把未推送的本地修改称为远端最新版本。

9. 2026-11-01现行评分已统一为P=80/(1+10e)、draft-3.11.0。当前正式后台工程包为internal-v6，两模型校准包revision3；80/15/5、P>=40、配额、噪声和真实规律不变。旧v5移至legacy保留5e历史，旧结果不自动覆盖或改写；starter-v2仍31文件。新v6参考只复用既有真值，没有重新模拟或验收。

10. 2026-11-02用户要求CUDA12.8及自选索引的pip安装格式。新增install_cuda128_envs.sh和README_CUDA12.8.txt：Python3.12/torch2.11+cu128/vLLM0.24源码/transformers5.8独立配置，旧0.32/cu129环境和ZIP保持。镜像地址通过参数传入；Torch包及上游源码仍需外网下载。先核验nvcc12.8和编译器，不把nvidia-smi的CUDA标签等同于已安装Toolkit。新环境不兼容旧0.32专用启动/检查脚本，使用其vllm serve直接启动；未远端验收，不声称模型已跑通。

11. 2026-11-02用户正式采纳轻量速度噪声1.1.0：sigma_v=1e-4*公开初速上限，每坐标/时刻/探针/新实验独立；首光同规则，缓存不重抽，初态及评分真值干净。当前模型校准ZIP为revision4、运行包为internal-v7；保留原r3及v6在legacy原字节追溯。新包只更新传感器、相关提示词/文案/源码摘要，复用旧干净验证数组与案例，不代表新的六公开＋九正式定义已全部接入旧运行包。prepare --refresh保护旧环境、日志、结果及CUDA12.8源码构建目录；远端已有解压目录须显式refresh才更新，不能只git pull后声称运行了新噪声。

12. 2026-11-02登录提示来自资料库认证，安装依赖与私有资料同步分开。公开主仓库scripts/bootstrap_cuda128.sh无需本仓库内容即可安装uv/CPU环境/源码vLLM CUDA12.8，并生成activate_cuda128.sh；README_CUDA12.8.txt已将此作为独立入口。sdist构建固定VLLM_VERSION_OVERRIDE，公开上游源码下载需要网络而非账号。旧安装器保留作历史，不把nvidia-smi标签等同Toolkit或基础检查等同模型验收。

13. 2026-11-02用户随后明确确认公开整个test，GitHub API修改及连接器只读核验均为public。匿名HTTPS clone/pull不再要求本仓库登录；写入仍需授权。历史ZIP内private/organizer-only标识保留作交付溯源，当前访问权限以GitHub仓库状态为准；不为更改可见性重写历史压缩包或校验值。

14. 2026-11-02实际部署已明确为联网CPU实例构建镜像，再启动完全无网的4H200实例；目标仍CUDA12.8。主仓库bootstrap新增--cpu-build-for h200固定SM90、CPU端不要求GPU/驱动，另行预下载FlashInfer0.6.12/cu128内核并在H200验收。环境、工具链、缓存建议放镜像包含的/opt目录，共享盘项目/模型另挂载。旧默认四卡安装器不适用于CPU制镜像；参见主仓库docs/H200_OFFLINE_SETUP.txt。未实际在远端构建/运行，不称已验收。

15. 2026-11-02用户确认正式与内部模拟每宇宙10分钟（600秒），从首次成功mission起计模型调用、实验和工具处理，模型加载另计，后续指挥部积分评分不占探索时限。当前两校准包r5、正式后台internal-v8、起步包starter-v3；旧r4/v7/v2原字节在legacy保留。新v8只继承旧干净案例与真值、更新时限及摘要，不改物理或声称新六公开＋九隐藏已迁移。请求等待受剩余会话预算约束且拒绝迟到action；旧结果保留原3600秒口径，不伪称已通过600秒。刷新已有解压目录须显式--refresh，不覆盖日志、结果或环境。

16. 2026-11-02用户已授权并完成整改，当前starter-v4（65文件）、两模型测试r6、runtime internal-v9。starter含六公开/可改LLM基线/完整Console生命周期/七模型/cu128新入口；runtime/public为同一公开kit，r6把完整public与正式源/profile平铺，兼容旧解压目录。旧v3/r5/v8原字节在legacy。最新九界与coverage已迁入并全量重生成干净参考；固定参数/噪声1.1/600/评分不变。隐藏team-export已停、导出CLI包括旧结果无条件拒绝，六公开记录仍可复用。当前入口为docs/QUICKSTART、scripts/serve_model.py和development_worlds.runner，旧0.32及表达式校准仅历史诊断，不作为基础框架。models目录/model-id/BF16-FP8已统一，保留venv Python路径；397BF16容量不足会拒绝。configure_runtime四步用真实设备/镜像/生成证据发布，不虚构远端验收。包CRC/hash/隔离CLI与旧refresh保护已过，公开179回归和15界75合成请求通过，未真实加载模型/GPU。

17. 2026-11-02用户更新长期远端路径为26-the-other-shore/fengkairui-25026下的DiscoverPhysics和test（见第5条）。现行校准包升r7、runtime升internal-v9-r2，仅更新可移植项目定位和当前部署路径；科学profile仍internal-v9，真实场、验证数组、600秒及评分不变，starter-v4保持原字节。r6和v9原包归档legacy，packages/SHA及refresh保护同步检查；不重跑物理积分、真实模型或API。README中的安装/解压路径均按新父目录，旧路径只保留作历史，不因项目迁移猜测Conda安装也已移动。

18. 2026-11-03修复安装镜像404和CUDA头文件/FindCUDA发现问题。starter-v6含72文件、runtime-direct-v1-r2含110文件，两校准包r9含145/146文件；三项新增助手随包提供。test根的install_cuda128_envs.sh仅委托同级canonical bootstrap，保留旧--test-root映射为--env-root，构建逻辑不另复制。指定镜像失败后仅单次官方PyPI回退；Python构建依赖先下载核验，CUDA编译仅CPU对象预检。r2只更新版本身份/源码摘要，所有原九界配置和干净参考保持原字节，r9同时保留direct-v1/internal-v9以安全刷新旧receipt。旧v5/r8/direct-v1在legacy完整保留；包校验、CPU模拟测试和现场H200安装验收分别记录，不因交付更新宣称GPU/模型已成功。外层install_all_dependencies.sh仅主项目提供，不在参赛者ZIP中。

19. 2026-11-05已完成三轮/三隐藏交付，48份归档SHA/CRC、104项科学/旧profile/干净参考原字节及四类旧包刷新保护通过，资料库36项回归通过。实际解压的starter-v10和runtime-r3以脚本化本机模型服务跑通六公开每界3调用共18次，三隐藏每界3调用共9次，law/claims与固定积分计分、权重/反馈独立复算通过；最终两契约文字修订后的包与已执行包保持执行/SDK/科学字节完全相同，回执保留实跑包摘要，不冒充新真实模型验收。无外部API、权重张量或GPU调用。

20. 2026-11-05正式交付改为指挥部私有环境加agent目录/models.json两路径。实际解压包以脚本化本机模型服务完成三隐藏9次调用、六公开18次调用，两个同底座不同训练绑定及附加adapter路径均被接收，固定积分/10e计分与反馈独立复算通过。无真实模型张量、GPU或Linux普通账号降权实测。最终对五份旧部署指南只添加历史兼容提示后重打包，执行/SDK/agent/科学字节与实跑包逐文件相同，保留实际执行包原摘要；四类刷新及52归档复核通过，当前protocol_e2e_validated仅表示上述工程链通过。
