# 测试资料库协作约定

最后更新：2026-11-02（北京时间）。

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
