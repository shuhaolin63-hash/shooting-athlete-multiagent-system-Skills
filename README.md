# 10米气步枪射击训练多智能体系统

> Shooting Athlete Multi-Agent System for 10m Air Rifle

## 项目简介

基于20篇PubMed学术论文和顶尖射击选手实操标准化框架，构建的一套完整10米气步枪射击训练多智能体系统。服务项目：男子10米气步枪 / 混合双人气步枪10米。

## 核心特性

- **15个智能体协作**：1个总调度 + 5个训练模块 + 3个通用智能体 + 6个团队角色
- **20篇学术论文支撑**：PubMed权威证据链，覆盖生物力学、神经科学、训练干预、心理训练
- **五维度量表评分**：基础定型/实弹射击/专项体能/高压心理/装备适配（各100分，总分500）
- **室内外场景区分**：针对10米气步枪（室内）和50米小口径（室外）差异化方案
- **可替代训练方案**：无靶场条件下的居家/室内替代训练
- **三种保障体制对比**：中国国家队（8-11人）/ 海外自费（5-6人）/ 协会共享（极简）
- **6个自动化脚本**：量表计算、训练达标、身体指标、团队审计、数据统计、报告输出
- **完整模板体系**：训练计划模板、复盘记录、赛前模拟方案、岗位职责说明书

## 完整目录结构

```
shooting-athlete-multiagent-system/
├── AGENTS.md                             # 全局智能体总注册表（15个智能体）
├── SKILL.md                              # 技能主入口
├── README.md                             # 本文件
│
├── agents/                               # 15个独立智能体定义（每个含agent.md + config.json）
│   ├── orchestrator-agent/               # 总调度智能体
│   ├── module1-aimless-foundation/       # 模块1：无弹基础定型
│   ├── module2-live-fire/                # 模块2：实弹射击实操
│   ├── module3-physical-fitness/         # 模块3：射击专项体能
│   ├── module4-mental-resilience/         # 模块4：赛场高压心理模拟
│   ├── module5-equipment-fitting/         # 模块5：枪械护具装备适配
│   ├── literature-support-agent/         # 文献支撑智能体
│   ├── scale-eval-agent/                 # 量表评估智能体
│   ├── data-calc-agent/                  # 数据计算智能体
│   ├── team-coaching/                    # 团队角色：技术教练组
│   ├── team-strength/                    # 团队角色：专项科研体能
│   ├── team-psychology/                  # 团队角色：运动心理保障
│   ├── team-medical/                     # 团队角色：医疗康复组
│   ├── team-armorer/                     # 团队角色：枪械装备技术师
│   └── team-logistics/                   # 团队角色：后勤综合保障
│
├── skills/
│   ├── shooting-training-scale/           # 主技能包
│   │   ├── SKILL.md                       # 技能定义
│   │   │
│   │   ├── assets/                        # 资产文件库
│   │   │   ├── tables/                    # 表格文件
│   │   │   │   ├── 选材身体指标表.xlsx      # 13项身体机能选材指标（4级阈值）
│   │   │   │   ├── 训练评分量表.csv         # 五大实操维度23项分级打分标准
│   │   │   │   ├── 团队配置对比表.xlsx      # 三类体制14岗位配置对比
│   │   │   │   └── 年度训练量化记录表.csv   # 每日训练数据记录模板
│   │   │   │
│   │   │   ├── diagrams/                  # 架构流程图、动作示意图
│   │   │   │   ├── agent协作架构.svg        # 15智能体任务流转链路
│   │   │   │   ├── 训练层级流程图说明.md    # 五层训练层级流程说明
│   │   │   │   ├── 射击五大实操训练层级流程图描述.md
│   │   │   │   ├── 国家队保障团队组织架构图描述.md
│   │   │   │   ├── 气步枪标准三姿站姿受力示意图描述.md
│   │   │   │   └── 枪口晃动误差分析示意图描述.md
│   │   │   │
│   │   │   ├── templates/                 # 训练方案、复盘文档模板
│   │   │   │   ├── 个人每日实操训练计划模板.md    # 零基础/省赛两套日程
│   │   │   │   ├── 训练复盘记录表.md              # 逐发弹道偏差记录
│   │   │   │   ├── 赛前高压模拟对抗方案模板.docx  # 噪音/落后/限时/混团模拟
│   │   │   │   ├── 团队人员分工岗位职责说明书.docx  # 11岗位完整权责规范
│   │   │   │   └── 射击运动员综合训练能力评估报告模板.docx  # 最终正式评估报告
│   │   │   │
│   │   │   ├── reference-images/           # 选手、装备参考图
│   │   │   │   ├── 选手训练参考图集说明.md
│   │   │   │   ├── 装备配件示意图集说明.md
│   │   │   │   └── 训练器材图集说明.md
│   │   │   │
│   │   │   ├── config-rules/               # 量表打分配置文件
│   │   │   │   ├── scale-scoring-rules.yaml   # 打分权重/扣分标准/晋级阈值
│   │   │   │   └── team-config-standard.json  # 团队标准岗位/人数/校验规则
│   │   │   │
│   │   │   └── audio-material/              # 赛场干扰音效素材（可选）
│   │   │       └── 赛场干扰音效素材包说明.md
│   │   │
│   │   ├── scripts/                        # 自动化Python脚本
│   │   │   ├── score_calc.py               # 量表总分计算、等级评级
│   │   │   ├── training_qualify.py         # 训练五大维度达标判定
│   │   │   ├── body_index_check.py          # 身体机能选材指标校验
│   │   │   ├── team_audit.py               # 射击保障团队完备度评分
│   │   │   ├── data_stat.py                # 训练数据统计、弹药/时长汇总
│   │   │   └── export_report.py            # 自动输出训练评估报告
│   │   │
│   │   └── references/                     # 参考文献库
│   │       ├── academic-papers.md           # 20篇PubMed论文完整引用
│   │       ├── reference-index.csv           # 文献索引总表（25条）
│   │       ├── domestic-sports-research/     # 国内中文文献
│   │       │   ├── 总局专项研究报告.md
│   │       │   ├── 高校体育核心期刊论文.md
│   │       │   ├── 硕博学位论文.md
│   │       │   └── 射击教学专著.md
│   │       ├── international-sci-literature/ # 国际外文SCI
│   │       │   ├── 运动视觉专项论文.md
│   │       │   ├── 高压疲劳训练研究.md
│   │       │   └── 欧美选手轻量化训练.md
│   │       ├── official-standard-whitepaper/ # 官方标准白皮书
│   │       │   ├── 智能弹道训练系统技术白皮书.md
│   │       │   ├── ISSF官方训练技术手册.md
│   │       │   └── 射击运动康复行业标准.md
│   │       └── athlete-case-materials/       # 运动员案例纪实
│   │           ├── 国内顶尖选手训练纪实.md
│   │           ├── 教练深度专访文字稿.md
│   │           └── 海外名将私人训练体系.md
│   │
│   └── shared-common/                      # 全Agent共享技能
│       └── SKILL.md
```

## 快速开始

1. 阅读 `AGENTS.md` 了解15个智能体架构与协作关系
2. 阅读 `SKILL.md` 了解核心框架与触发条件
3. 根据需求调用对应智能体：

| 需求 | 推荐智能体 |
|------|----------|
| 无弹定型训练 | module1-aimless-foundation |
| 实弹射击指导 | module2-live-fire |
| 体能训练方案 | module3-physical-fitness |
| 心理抗压训练 | module4-mental-resilience |
| 装备适配调试 | module5-equipment-fitting |
| 教练组配置建议 | team-coaching |
| 体能团队建议 | team-strength |
| 心理保障建议 | team-psychology |
| 医疗康复方案 | team-medical |
| 枪械调试方案 | team-armorer |
| 后勤保障方案 | team-logistics |
| 学术论文检索 | literature-support-agent |
| 量化评分评估 | scale-eval-agent |
| 数据计算分析 | data-calc-agent |

## 自动化脚本使用

| 脚本 | 对应智能体 | 功能 |
|------|----------|------|
| score_calc.py | Scale-Eval-Agent | 五维度加权打分，自动判定零基础/省赛/国青/国家队等级 |
| training_qualify.py | Training-Analysis-Agent | 校验训练是否达标（空扣次数、定型时长、实弹量等） |
| body_index_check.py | Data-Calc-Agent | 校验选材指标（静息心率、平衡时长、核心耐力等） |
| team_audit.py | Team-Structure-Agent | 审计团队完备度，检测岗位缺失 |
| data_stat.py | Data-Calc-Agent | 统计月/年训练数据、失误类型、进步曲线 |
| export_report.py | Orchestrator-Agent | 一键生成综合训练评估报告 |

## 保障团队体制对比

| 角色 | 国家队A（8-11人） | 海外自费B1（5-6人） | 协会共享B2（极简） |
|------|-------------------|-------------------|-------------------|
| 技术教练组 | 主教练+1-2助理+启蒙=3-4人 | 外籍总教练=1人 | 无专属 |
| 体能科研 | 体能主教练+助理=2人 | 私人体能师=1人 | 无专属 |
| 心理保障 | 专职心理老师=1人 | 运动心理医生=1人 | 无 |
| 医疗康复 | 队医+2理疗师=3人 | 私人康复理疗师=1人 | 大赛临时1队医 |
| 枪械师 | 专属枪械师=1人 | 枪械技师=1人 | 无 |
| 后勤数据 | 生活管理员+数据分析师=2人 | 生活管家=1人 | 无 |
| **合计** | **8-11人，大赛扩充至12-14人** | **5-6人，全部自费** | **日常无团队** |

## 文献体系

- **PubMed SCI论文**：20篇，覆盖系统综述、生物力学、神经生理、训练干预、心理训练（见 `references/academic-papers.md`）
- **国内中文文献**：总局研究报告、高校核心期刊、硕博论文、教学专著（见 `references/domestic-sports-research/`）
- **国际SCI文献**：运动视觉、ML疲劳检测、轻量化训练（见 `references/international-sci-literature/`）
- **官方标准**：智能弹道白皮书、ISSF手册、康复行业标准（见 `references/official-standard-whitepaper/`）
- **运动员案例**：黄雨婷/杨倩/盛李豪训练纪实、教练访谈、海外名将方案（见 `references/athlete-case-materials/`）

## 注意事项

1. 所有枪械操作必须遵守安全规程
2. 训练方案需根据个人情况调整
3. 关键动作修正建议在教练指导下进行
4. 学术论文版权归原作者和出版方所有
5. 参考图片和音效素材需自行收集，说明文件已提供详细清单和规格

## 版权声明

本项目为知识整理与学习参考，仅供学习交流使用，不得用于商业目的。
