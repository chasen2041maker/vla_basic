# Guided Reference 001A

这是一个零第三方依赖的教学 baseline。

## Run

```powershell
python run_eval.py
python -m unittest discover -s tests -v
```

预期：

```text
4 / 6 PASS
2 / 6 FAIL
```

## 为什么故意只有 4/6

`BaselineValidator` 只检查：

- camera name 是否重复；
- future trajectory timestamp 是否严格递增。

它故意不检查：

- camera 与 reference time 的最大偏差；
- future trajectory 是否真的位于 reference time 之后。

这两个 gap 用于学习“结构合法但语义错误”。

## Import Path

`run_eval.py` 和 tests 都是自包含运行，不需要安装 package。

## 教学简化

- 没有真实图像，只保存 `image_ref`；
- 只有二维位置和 yaw；
- 没有地图、目标、交通参与者和控制信号；
- threshold 不代表量产系统标准；
- JSON 不是最终数据集格式。

这些简化用于隔离第一课的问题：时间契约。
