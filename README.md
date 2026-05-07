# BSE Exposure Simulation

这个项目用于生成 5x5 主场内不同写入密度下的子场写入顺序，并计算每个束斑点对应的高斯背散射贡献。每个密度版本放在独立文件夹中，脚本会导出 Excel 结果和若干写入顺序示意图。

## 目录结构

```text
bse_exp/
├── 6/
│   └── calculation_code_6.py
├── 50/
│   └── calculation_code_50.py
├── 83/
│   └── calculation_code_83.py
├── 99/
│   └── calculation_code_99.py
└── README.md
```

## 密度版本

| 文件夹 | 普通子场点阵 | 含义 |
| --- | --- | --- |
| `6` | `9 x 9` | 低密度版本，约 `6.25%` |
| `50` | `36 x 18` | 中密度版本，约 `50%` |
| `83` | `36 x 30` | 高密度版本，约 `83.33%`，y 方向每 6 行空 1 行 |
| `99` | `36 x 36` | 近似全覆盖版本 |

主场都是 `5 x 5` 个子场，子场写入顺序为从右上角开始的逆时针螺旋顺序。

## 子场逻辑

前 24 个子场使用普通写入模式。

第 25 个子场使用特殊写入模式：

1. 左侧普通区域
2. 中间王字形区域
3. 右侧普通区域

其中中间王字形的逻辑保持独立；左右普通区域会跟随对应密度版本使用相同的普通子场采样方式。

## 输出文件

每个密度文件夹运行脚本后，会生成类似下面的文件：

| 文件 | 说明 |
| --- | --- |
| `exported_results_5x5_spiral.xlsx` | 所有束斑点的计算结果 |
| `subfield_writing_order.png` | 5x5 主场子场写入顺序图 |
| `normal_subfield_order_subfield1.png` | 普通子场内部写入顺序图 |
| `wang_pattern_order_subfield25.png` | 第 25 个特殊子场写入顺序图 |

## 运行方式

先安装依赖：

```bash
pip install numpy scipy pandas matplotlib openpyxl
```

进入对应密度文件夹后运行脚本，例如：

```bash
cd 83
python calculation_code_83.py
```

其它密度版本同理：

```bash
cd 6
python calculation_code_6.py

cd 50
python calculation_code_50.py

cd 99
python calculation_code_99.py
```

## 主要参数

脚本中的核心参数包括：

| 参数 | 说明 |
| --- | --- |
| `L_sub` | 单个子场尺寸，当前为 `9.0 um` |
| `MAIN_N` | 主场子场数量，当前为 `5`，即 `5 x 5` |
| `beam_L` | 束斑尺寸，当前为 `0.25 um` |
| `beta` | 高斯背散射半径参数 |
| `x_center`, `y_center` | 主场中心坐标 |

## Git 注意事项

`.idea/` 已经通过 `.gitignore` 忽略，PyCharm/IDE 本地配置不会进入仓库。

生成的 Excel 和 PNG 文件如果只是临时结果，可以不提交；如果需要保留某次计算结果，再手动加入 Git。
