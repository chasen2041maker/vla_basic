# 06｜数学、Linux、C++不是在简历上打三个勾

材料补充：2026-09-27。以下是局部工程例子，不是新的驾驶程序；只在需要时使用，不改变 [当前实践课题](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)。

## 先从一个你已经理解的问题开始

上一讲算了世界点转自车坐标。将同一段计算放到 C++，不是为了重学全部语言，而是理解将来数据处理、控制或模型后处理跨语言时，单位、接口和错误怎样保持一致。它可能处在整车链路的定位/感知几何或规划输出处理处；本例并未接入任何车辆。

C++ 的 `double` 不会检查“这个数到底是度还是弧度”。编译通过也不会告诉你公式是否正确。因此需要手算例子、坏输入、退出码和测试，而不只是成功生成可执行文件。

## 可编译的最小例子

将以下代码保存到临时目录的 `geometry_check.cpp`，与上一讲的 Python 例子放在一起。VS Code 用 Ctrl+P 找该文件；它不是本仓库已有的部署入口。

```cpp
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

using Vec2 = std::array<double, 2>;

Vec2 world_to_ego(const Vec2& point, const Vec2& origin, double yaw_rad) {
    for (double value : {point[0], point[1], origin[0], origin[1], yaw_rad}) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument("non-finite input");
        }
    }
    const double dx = point[0] - origin[0];
    const double dy = point[1] - origin[1];
    const double c = std::cos(yaw_rad), s = std::sin(yaw_rad);
    return {c * dx + s * dy, -s * dx + c * dy};
}

void check_pair(const Vec2& actual, const Vec2& expected) {
    for (std::size_t i = 0; i < actual.size(); ++i) {
        if (!std::isfinite(actual[i]) || std::abs(actual[i] - expected[i]) > 1e-9) {
            throw std::runtime_error("coordinate check failed");
        }
    }
}

int main(int argc, char** argv) {
    try {
        if (argc > 2 || (argc == 2 && std::string(argv[1]) != "--inject-degrees")) {
            throw std::invalid_argument("usage: geometry_check [--inject-degrees]");
        }
        // 故障模式故意把 90 度当成 90 弧度，正例期望保持不变。
        const double yaw = argc == 2 ? 90.0 : std::acos(-1.0) / 2.0;
        check_pair(world_to_ego({10.0, 5.0}, {10.0, 0.0}, yaw), {5.0, 0.0});
        check_pair(world_to_ego({10.0, 5.0}, {10.0, 0.0}, 0.0), {0.0, 5.0});
        bool rejected = false;
        try {
            world_to_ego({std::numeric_limits<double>::quiet_NaN(), 5.0},
                         {10.0, 0.0}, 0.0);
        } catch (const std::invalid_argument&) {
            rejected = true;
        }
        if (!rejected) throw std::runtime_error("invalid input was accepted");
        std::cout << "geometry checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
```

`std::array<double,2>` 是固定两个数；`const Vec2&` 表示只读地引用传入对象；返回一个新的二维数组，不修改原输入。异常在 main 中被捕获并变成非零退出码，错误信息写到 stderr。这里不使用会被 `NDEBUG` 关闭的 C++ assert 作为唯一检查。

在 **Linux 或已有 C++ 工具链的 WSL** 中，从保存目录运行；以下是 Bash 命令，不是 PowerShell：

```bash
g++ --version
g++ -std=c++17 -Wall -Wextra -Werror -O0 -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  geometry_check.cpp -o geometry_check
./geometry_check
# 故障模式应输出 coordinate check failed，退出码应为 1。
./geometry_check --inject-degrees
printf 'exit=%s\n' "$?"
```

正常预期 `geometry checks passed` 且退出码 0。这里 sanitizer 用于帮助发现内存/未定义行为问题；**度/弧度错误由业务数值检查发现，不是 sanitizer 自动理解了单位**。选项说明见 [GCC 官方手册](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)，读取于 2026-09-27。

本轮维护者在 Linux、g++ 14.2.0 上运行了正常与故障分支；Windows/WSL 本机、其他编译器和 IDE 调试未验证。缺少工具链时不要为了当前动作源码课立刻重装环境。

## 预测、修改、定位

先不用运行，解释自车 yaw=0 与 π/2 时同一个点为什么分别得到 `(0,5)` 和 `(5,0)`。再运行正常分支，并用上一讲 Python 实现核对相同例子。

故障模式没有改公式，只把 90 当作弧度传入。看到失败后，应该追查输入单位而不是放宽误差到能通过。下一步可在临时副本故意漏掉平移或改错一个旋转符号，先预测哪条检查会失败，再证实。后两种修改是练习建议，本轮没有冒充已经替学习者完成。

此例只说明局部计算和报错机制；不证明 C++ 大型工程、并发、内存管理、车辆实时性或车端部署已经掌握。

## 接下来按岗位补到什么深度

| 基础 | 近期可见证据 | 选择相应岗位后继续深化 |
| --- | --- | --- |
| 数学 | 相对速度/时间、量纲、正反坐标、投影、误差和抽样；正常与坏例子都能解释 | 规控：离散动力学、稳定性/优化与约束；算法：梯度、优化、概率、视觉与时序；评测：统计、采样与指标偏差 |
| Linux | cwd/路径、依赖/解释器、stdout/stderr、退出码、进程和资源记录；从日志定位一次实际错误 | 批量任务、权限、容器、资源瓶颈；不以会复制 Docker 命令代替排错 |
| C++ | 读改一个有单位约定的函数、编译、检查输入、解释失败 | 按 JD 到真实模块的 CMake/CTest、调试栈、对象生命周期、边界/内存错误；部署或规控还需集成与性能 |
| 模型调试 | shape/dtype/device/mask、可复现小样本、保存重载和非有限数定位 | 数据装载、计算、通信或 runtime 瓶颈；优化前后数值和行为对照 |

这些深化工程尚未由本例提供。它们是明确的补齐目标，不是把名词抄进简历。

## 性能报告怎样避免虚假“更快”

先固定硬件、模型/数据/config、输入尺寸、batch、精度、runtime、预热与测量方式。分别测预处理、推理、解码和控制链路；异步设备计时需正确同步。报告分布与异常，不只报最好的一次或单个平均数。

压缩前后不仅看模型误差，还看选定驾驶场景的行为变化。超时、旧观测、无效输出如何检测、拒绝或降级，需要独立测试；不能宣称在本教学例子中完成了量产功能安全。具体车辆执行器、CAN/诊断和实车集成按目标 JD 再引入，不把所有岗位都叠加成底盘专家路线。

返回 [能力决策](../SKILL_GAP_MATRIX.md)、[交付标准](../CURRICULUM_STANDARD.md)与 [讲义目录](README.md)。
