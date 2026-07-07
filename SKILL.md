---
name: "shooting-athlete-multiagent"
description: "10米气步枪射击训练多智能体系统，涵盖动作要领、室内外场景区分、体能/心理/恢复训练、保障团队架构、学术论文支撑。当用户提到射击训练、气步枪、10米气步枪、射击技巧、射击评分、射击体能、射击心理、射击团队、射击装备时触发。"
---

# 10米气步枪射击训练多智能体系统

> 基于20篇PubMed学术论文 + 顶尖射击选手实操标准化框架 + 保障团队完整结构
> 服务项目：男子10米气步枪 / 混合双人气步枪10米

## 技能概述

本技能提供一套完整的10米气步枪射击训练体系，通过15个智能体协作架构，覆盖射击运动的全部核心维度：

| 类别 | 智能体 | 职责 |
|------|--------|------|
| **总调度** | orchestrator-agent | 任务路由、智能体协调、输出质量控制 |
| **训练模块** | module1-aimless-foundation | 模块1：无弹基础定型（姿态/稳定/瞄准/击发/呼吸） |
| **训练模块** | module2-live-fire | 模块2：实弹射击实操（常规/决赛高压/抗干扰/团体协同/复盘） |
| **训练模块** | module3-physical-fitness | 模块3：射击专项体能（核心静力/肩颈静力/平衡/心肺/放松） |
| **训练模块** | module4-mental-resilience | 模块4：赛场高压心理模拟（对抗/可视化/疲劳/仪式固化） |
| **训练模块** | module5-equipment-fitting | 模块5：枪械护具装备适配（枪械调试/皮衣调整/新规适配） |
| **通用** | literature-support-agent | 20篇PubMed学术论文检索与权威论证 |
| **通用** | scale-eval-agent | 五维度量化打分评估与进步追踪 |
| **通用** | data-calc-agent | 身体指标计算、训练数据分析 |
| **团队角色** | team-coaching | 技术教练组（主教练+助理+启蒙教练） |
| **团队角色** | team-strength | 专项科研体能团队（体能主教练+助理+科研） |
| **团队角色** | team-psychology | 运动心理保障（专职心理老师/心理医生） |
| **团队角色** | team-medical | 医疗康复组（队医+2名康复理疗师） |
| **团队角色** | team-armorer | 枪械装备技术师（校准/改造/定制/保养） |
| **团队角色** | team-logistics | 后勤综合保障（生活管理+数据分析+特殊增量） |

## 触发条件

### 直接触发
- "射击训练"、"气步枪"、"10米气步枪"、"10m air rifle"
- "射击技巧"、"射击姿势"、"射击要领"
- "射击评分"、"射击评估"、"射击量表"
- "射击体能"、"射击心理"、"射击恢复"
- "射击团队"、"射击教练"、"射击保障"

### 间接触发
- "步枪稳定性"、"枪口晃动"、"瞄准精度"
- "击发控制"、"扳机控制"、"屏息击发"
- "射击心率"、"呼吸控制射击"、"射击脑电"
- "射击生物力学"、"姿态稳定"、"射击训练生物反馈"
- "混合团体"、"混团射击"、"双人射击"
- "射击皮衣"、"射击护具"、"枪械调试"
- "射击心理训练"、"抗压训练"、"射击可视化"

### 场景触发
- 用户在制定射击训练计划
- 用户在分析射击技术动作
- 用户在评估射击训练效果
- 用户在组建射击训练团队
- 用户在搜索射击相关文献

## 知识库结构

```
shooting-athlete-multiagent-system/
├── AGENTS.md                         # 全局智能体总注册表（15个智能体）
├── SKILL.md                          # 技能主入口
├── README.md                         # 项目介绍
├── agents/                           # 15个独立智能体定义
│   ├── orchestrator-agent/           # 总调度智能体
│   ├── module1-aimless-foundation/   # 模块1：无弹基础定型
│   ├── module2-live-fire/            # 模块2：实弹射击实操
│   ├── module3-physical-fitness/     # 模块3：射击专项体能
│   ├── module4-mental-resilience/     # 模块4：赛场高压心理模拟
│   ├── module5-equipment-fitting/    # 模块5：枪械护具装备适配
│   ├── literature-support-agent/      # 文献支撑智能体
│   ├── scale-eval-agent/             # 量表评估智能体
│   ├── data-calc-agent/              # 数据计算智能体
│   ├── team-coaching/                # 团队角色：技术教练组
│   ├── team-strength/                # 团队角色：专项科研体能
│   ├── team-psychology/              # 团队角色：运动心理保障
│   ├── team-medical/                 # 团队角色：医疗康复组
│   ├── team-armorer/                 # 团队角色：枪械装备技术师
│   └── team-logistics/               # 团队角色：后勤综合保障
├── skills/                           # 业务技能包
│   ├── shooting-training-scale/      # 射击训练评估主技能
│   │   ├── SKILL.md
│   │   ├── references/academic-papers.md  # 20篇PubMed论文
│   │   ├── scripts/
│   │   └── assets/
│   └── shared-common/                # 全Agent共享技能
│       └── SKILL.md
└── README.md
```

## 核心框架：射击表现决定因素（学术验证）

基于 Spancken et al. (2021) 系统综述和 Ihalainen et al. (2016) 研究，射击表现由四大类因素决定：

### 技术协调类（权重最高，解释80%+得分方差）

| 核心因素 | 权重（精英选手） | 学术证据 |
|----------|-----------------|----------|
| 握持稳定性（Stability of Hold） | ~36% | Ihalainen 2016; Lang & Zhou 2024 |
| 击发清洁度（Cleanness of Triggering） | ~25% | Ihalainen 2016; Köykkä 2022 |
| 瞄准精度（Aiming Accuracy） | ~12% | Spancken 2021; Ihalainen 2016 |
| 击发时机（Timing of Triggering） | ~8% | Ihalainen 2016 |
| 瞄准时间（Aiming Time） | 辅助指标 | Ihalainen 2016 |

### 生理类

| 因素 | 与表现关系 | 学术证据 |
|------|----------|----------|
| 姿态平衡 | 间接影响（通过握持稳定性传递，R=0.55） | Ihalainen 2016; Era 1996 |
| 心率 | 精英选手中与得分无显著直接相关 | Konttinen 1998; Spancken 2021 |
| 呼吸控制 | 可训练，6周训练即显著改善成绩 | Park 2019 |
| 脑电活动（额叶theta波） | 专家在击发前3秒theta波持续增强 | Doppelmayr 2008 |

### 心理类

| 因素 | 作用 | 学术证据 |
|------|------|----------|
| 注意力聚焦 | 专家能在击发瞬间精确提升注意力 | Doppelmayr 2008 |
| 心理灵活性 | ACPT方案有效提升精英射手表现 | Hwang 2025 |
| 压力管理 | 高压环境下表现差异的关键 | Konttinen 1998 |
| 决策能力 | 生物反馈通过改善决策提升表现 | Mullineaux 2012 |

### 人体测量类

| 因素 | 作用 | 备注 |
|------|------|------|
| 身体比例 | 影响持枪框架舒适度 | 通过装备适配调整 |
| 手指长度/力量 | 影响扳机控制 | 通过训练补偿 |

## 使用方式

### 新手入门路径
```
1. 调用 scale-eval-agent 进行基础评估
2. 调用 module1-aimless-foundation 进行无弹基础定型训练
3. 调用 data-calc-agent 计算个人身体指标基线
4. 调用 team-coaching 了解教练组配置，调用 team-logistics 了解后勤保障
```

### 进阶提升路径
```
1. 调用 scale-eval-agent 进行阶段评估
2. 调用 module2-live-fire 进行实弹训练
3. 调用 module3-physical-fitness 进行体能训练
4. 调用 literature-support-agent 获取针对性文献
5. 调用 data-calc-agent 进行训练数据分析
```

### 比赛准备路径
```
1. 调用 module4-mental-resilience 进行心理抗压训练
2. 调用 module5-equipment-fitting 进行装备适配
3. 调用 scale-eval-agent 进行模拟评分
4. 调用 team-psychology 进行心理保障
5. 调用 team-armorer 进行枪械赛前检查
```

## 室内 vs 室外场景区分

| 维度 | 室内10米气步枪 | 室外50米小口径 |
|------|---------------|---------------|
| 环境 | 恒温、无风、光照可控 | 温差大、侧风、逆光、光线变化 |
| 核心干扰 | 灯光反射、观众噪音 | 风偏、光线角度、温度变化 |
| 瞄准补偿 | 基本无环境补偿 | 风偏修正、光线适应、温度弹道变化 |
| 训练侧重点 | 精细技术动作、心理稳定 | 环境适应能力、快速调整能力 |
| 装备差异 | 轻量化气步枪、专用射击服 | 重量更大、更多防护装备 |
| 替代方案 | 居家无弹定型训练同样有效 | 需要更多室外实地训练 |

## 可替代训练方案

当无法使用标准靶场时：

| 标准训练 | 室内替代 | 居家替代 |
|----------|---------|---------|
| 实弹射击 | 激光射击训练器 | SCATT/MegaLink空枪训练系统 |
| 靶纸实弹 | 电子靶投影 | 墙壁贴纸靶+激光笔 |
| 持枪定型 | 枪械配重模拟 | 瓶装水/沙袋负重定型 |
| 呼吸控制 | 呼吸训练APP | 腹式呼吸计数练习 |
| 心理训练 | VR模拟赛场 | 冥想可视化音频引导 |
| 体能训练 | 室内健身房 | 居家自重训练 |

## 关键执行原则

1. **动作质量优先于数量**：每一次空枪练习都必须是正确的动作模式
2. **数据驱动决策**：每一发都记录，每一次训练都有数据
3. **个体化分析**：精英水平错误分析必须个体化（Ball 2003）
4. **渐进超负荷**：体能和训练量逐步增加，避免过度训练
5. **心理训练日常化**：不是比赛前才做心理准备，而是每日必练
6. **装备与人合一**：枪械和护具是身体的延伸，必须反复适配

## 学术论文引用（核心20篇）

详见 `skills/shooting-training-scale/references/academic-papers.md`

1. Spancken et al. 2021 - PLoS One - 系统综述（14篇文献，268名受试者）
2. Ihalainen et al. 2016 - Scand J Med Sci Sports - 精英气步枪表现决定因素
3. Lang & Zhou 2024 - Sports Biomech - 中国国家队选手表现分析
4. Era et al. 1996 - J Biomech - 姿态稳定与技能水平
5. Ball et al. 2003 - J Sports Sci - 个体化身体晃动分析
6. Ihalainen et al. 2016 - Int J Sports Physiol Perform - 技术测试与比赛成绩关系
7. Doppelmayr et al. 2008 - Neuropsychologia - 额叶theta波专家新手差异
8. Konttinen et al. 1998 - J Sports Sci - 击发前心率模式
9. Konttinen et al. 1993 - J Sports Sci - 慢脑波与射击成功
10. Konttinen et al. 2000 - Scand J Med Sci Sports - 瞄准程序与脑电耦合
11. Mullineaux et al. 2012 - Appl Ergon - 实时生物反馈训练效果
12. Mononen et al. 2003 - J Sports Sci - 增强型KP反馈促进学习
13. Park et al. 2019 - J Sport Rehabil - 6周平衡+呼吸训练效果
14. Sadowska et al. 2019 - J Sports Sci - 姿态平衡与步枪稳定性关系
15. Köykkä et al. 2022 - Scand J Med Sci Sports - 表现决定因素直接/间接效应
16. Köykkä et al. 2021 - Scand J Med Sci Sports - 瞄准策略影响表现
17. Hwang et al. 2025 - Behav Sci - ACPT心理训练方案验证
18. Lee & Shin 2025 - Med Sci Monit - tDCS+核心稳定提升射击
19. Hrysomallis 2011 - Sports Med - 平衡能力与运动表现综述
20. Zemková & Zapletalová 2022 - Front Physiol - 核心稳定性与运动表现

## 视频来源

- ISSF官方教学频道：https://www.issf-sports.org/
- 中国射击协会官方资源
- SCATT训练系统教程：https://scatt.com/

## 注意事项

1. **安全第一**：所有枪械操作必须遵守安全规程，空枪训练也需安全检查
2. **个性化调整**：每个人的身体条件不同，需要根据自己情况调整训练方案
3. **循序渐进**：从无弹定型开始，不要急于实弹
4. **结合实战**：训练要结合比赛情境模拟
5. **专业指导**：关键动作修正建议在教练指导下进行
6. **定期体检**：射击专项体能训练需关注肩颈劳损

## 版权声明

本项目为知识整理与学习参考，学术论文版权归原作者和出版方所有。仅供学习交流使用，不得用于商业目的。
