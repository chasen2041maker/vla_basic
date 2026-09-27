# Frontier Radar — Autonomous Driving VLA

最后核对：2026-08-28

这份文件记录快速变化的模型、工具和产业方向。稳定知识放在课程和 labs，不在这里重复。

状态：

```text
IGNORE  当前不投入
WATCH   跟踪，不进入主线
TRIAL   安排小实验
ADOPT   作为主线工具或基准
```

## 当前雷达

| 方向 / 项目 | 状态 | 为什么 | 当前行动 |
|---|---|---|---|
| XPENG 第二代 VLA | WATCH | 目标公司方向的重要系统参考，但完整训练栈和量产代码未公开 | 学习公开输入、动作、延迟和闭环信号，不声称复现 |
| XPENG X-World | WATCH | 已公开用于闭环仿真、在线 RL、数据生成和模型评估 | Lab 012 前只理解作用，不提前做重型复现 |
| FastDriveVLA / token pruning | WATCH | 直接关联车端视觉 token 效率和部署 | Lab 010 做公开可验证的代理实验 |
| XPENG 数据价值岗位能力 | WATCH | 说明数据分析、价值评估、场景发现和数据流转是现实桥梁能力 | 在 Lab 001/006/007 增加数据价值证据 |
| NAVSIM | ADOPT | 公开、可复现的驾驶规划评测主线 | Lab 007 |
| AutoVLA | TRIAL | 公开 Driving VLA 候选，可用于 action token 与推理实验 | Lab 008/009 前重新核对 commit 和许可 |
| CARLA | WATCH | 交互式闭环价值高，但环境重 | Lab 006 后按需要引入 |
| nuPlan devkit | WATCH | 规划数据和仿真生态的重要基础 | 按 NAVSIM / evaluator 需要使用 |
| World Model + Online RL | WATCH | 方向重要，但依赖闭环 evaluator 和 safety | Lab 012，不提前背算法名 |
| Robot Manipulation VLA | IGNORE | OpenVLA、π0、LeRobot 的机械臂知识不是当前主线 | 仅在动作表示类比时引用 |
| 自建真实车辆实验 | IGNORE | 安全、合规和成本不适合作为个人验收 | 使用公开数据、合成实验和仿真 |

## 官方与公开来源

### XPENG

- 27 届 VLA/VLM 算法岗位：<https://xiaopeng.jobs.feishu.cn/campus/position/7658239744397347110/detail>
- 27 届数据价值算法岗位：<https://xiaopeng.jobs.feishu.cn/campus/position/7658239755088447770/detail>
- 大模型算法工程师（智驾/机器人）：<https://xiaopeng.jobs.feishu.cn/campus/m/position/7668513578471475462/detail>
- 世界模型及环境感知岗位：<https://xiaopeng.jobs.feishu.cn/campus/m/position/7658239755087759642/detail>
- X-World：<https://www.xiaopeng.com/news/company_news/5548.html>
- FastDriveVLA：<https://www.xiaopeng.com/news/company_news/5526.html>

### Public Reproduction Targets

- NAVSIM：<https://github.com/autonomousvision/navsim>
- AutoVLA：<https://github.com/ucla-mobility/AutoVLA>

## 进入主线前的检查

任何新模型或框架进入课程前，记录：

```text
检查日期
官方来源
代码 commit / release
权重是否公开
数据许可
最低硬件
能否只跑推理
能否在 mini 数据上评测
输入时间与坐标契约
action 输出语义
评测协议
延迟和资源要求
我是否亲自验证
```

“读过论文”“看过 Demo”或“公司宣传效果很好”不能把状态改为 `ADOPT`。

## 更新日志

| 日期 | 变化 | 依据 |
|---|---|---|
| 2026-08-28 | 路线从 lab-first 改为 role-driven、system-first；加入数据价值、无 Agent 调试、世界模型闭环和车端效率信号 | 公开岗位与官方技术资料 |
| 2026-08-27 | 仓库从机器人操作 VLA 重构为自动驾驶 VLA | 官方项目与公开仓库 |
