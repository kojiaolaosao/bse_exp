import numpy as np
from scipy.special import erf
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体，Windows 常见


# =====================
# 画出 5x5 主场子场写入顺序图
# =====================
def plot_subfield_writing_order(subfield_order, MAIN_N, save_name="subfield_writing_order.png"):
    """
    画出主场 5x5 子场的写入顺序
    subfield_order: [(row, col), ...]
        row = 0 表示最下方
        col = 0 表示最左方
    """

    order_map = np.zeros((MAIN_N, MAIN_N), dtype=int)

    # 把写入顺序编号填入矩阵
    for idx, (row, col) in enumerate(subfield_order, start=1):
        order_map[row, col] = idx

    fig, ax = plt.subplots(figsize=(7, 7))

    # 画网格
    ax.set_xlim(0, MAIN_N)
    ax.set_ylim(0, MAIN_N)
    ax.set_aspect("equal")

    ax.set_xticks(np.arange(0, MAIN_N + 1, 1))
    ax.set_yticks(np.arange(0, MAIN_N + 1, 1))
    ax.grid(True, linewidth=1.2)

    # 写入每个子场的编号
    for row in range(MAIN_N):
        for col in range(MAIN_N):
            order_id = order_map[row, col]

            ax.text(
                col + 0.5,
                row + 0.5,
                str(order_id),
                ha="center",
                va="center",
                fontsize=18,
                fontweight="bold"
            )

    # 画箭头表示写入方向
    for k in range(len(subfield_order) - 1):
        row1, col1 = subfield_order[k]
        row2, col2 = subfield_order[k + 1]

        x1, y1 = col1 + 0.5, row1 + 0.5
        x2, y2 = col2 + 0.5, row2 + 0.5

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=1.8,
                shrinkA=15,
                shrinkB=15
            )
        )

    ax.set_title("5x5 主场子场写入顺序：右上角开始，逆时针螺旋", fontsize=14)

    ax.set_xlabel("Subfield Column")
    ax.set_ylabel("Subfield Row")

    # 坐标标签从 1 开始显示
    ax.set_xticks(np.arange(0.5, MAIN_N, 1))
    ax.set_yticks(np.arange(0.5, MAIN_N, 1))
    ax.set_xticklabels(np.arange(1, MAIN_N + 1))
    ax.set_yticklabels(np.arange(1, MAIN_N + 1))

    plt.tight_layout()
    plt.savefig(save_name, dpi=300)
    plt.show()

    print(f"主场写入顺序图已保存：{save_name}")


# =====================
# 高斯积分，使用全局坐标
# =====================
def gaussian_integral(cx, cy):
    """
    对以 (cx, cy) 为中心的 beam_L × beam_L 小方形区域
    积分中心在主场中心 (x_center, y_center)
    """

    x1, x2 = cx - half_L, cx + half_L
    y1, y2 = cy - half_L, cy + half_L

    term_x = erf((x2 - x_center) / beta) - erf((x1 - x_center) / beta)
    term_y = erf((y2 - y_center) / beta) - erf((y1 - y_center) / beta)

    return 0.25 * term_x * term_y


# =====================
# 单个子场内部扫描顺序
# =====================
def generate_one_subfield(subfield_id, sub_row, sub_col, global_start_id):
    """
    生成一个子场内部的写入顺序。

    sub_row: 子场所在行，0 表示最下方，4 表示最上方
    sub_col: 子场所在列，0 表示最左方，4 表示最右方

    global_start_id: 当前全局编号起始值
    """

    results = []

    # 当前子场左下角全局坐标
    x_offset = sub_col * L_sub
    y_offset = sub_row * L_sub

    # 9行 → 分3个区域，每个区域3行
    regions = [
        range(0, 12),  # 区域1
        range(12, 24),  # 区域2
        range(24, 36)  # 区域3
    ]

    # 区域1：从下到上
    # 区域2：从上到下
    # 区域3：从下到上
    region_scan_dirs = [
        "up",
        "down",
        "up"
    ]

    beam_id_in_subfield = 1
    global_id = global_start_id

    for region_idx, rows in enumerate(regions):

        direction = region_scan_dirs[region_idx]

        if direction == "up":
            y_order = range(2 * N)
        else:
            y_order = reversed(range(2 * N))

        for j in y_order:
            for i in rows:
                x_local = x_list_local[i]
                y_local = y_list_local[j]

                x_global = x_offset + x_local
                y_global = y_offset + y_local

                value = gaussian_integral(x_global, y_global)

                results.append({
                    "global_id": global_id,
                    "subfield_id": subfield_id,
                    "sub_row": sub_row + 1,
                    "sub_col": sub_col + 1,
                    "beam_id_in_subfield": beam_id_in_subfield,
                    "x_global": x_global,
                    "y_global": y_global,
                    "x_local": x_local,
                    "y_local": y_local,
                    "value": value
                })

                global_id += 1
                beam_id_in_subfield += 1

    return results, global_id


# =====================
# 第25个子场：左边普通区域 + 王字形 + 右边普通区域
# =====================
def generate_wang_pattern_subfield(
        subfield_id,
        sub_row,
        sub_col,
        global_start_id,
        cell_L=0.25,
):
    """
    生成第25个子场内部的特殊写入顺序：

    1. 左边区域：27个点，和普通子场第一区域一样
    2. 中间区域：王字形，保持原来的王字形写入逻辑
    3. 右边区域：27个点，和普通子场第三区域一样

    注意：
    - 王字形代码本身不改动
    - 左右两边普通区域仍使用原来 9x9 子场的点位
    - 左边区域对应普通子场的 range(0, 3)
    - 右边区域对应普通子场的 range(6, 9)
    """

    results = []

    # 当前子场左下角全局坐标
    x_offset = sub_col * L_sub
    y_offset = sub_row * L_sub

    global_id = global_start_id
    beam_id_in_subfield = 1

    # =========================================================
    # 1. 左边区域：27个点，和普通子场第一区域一样
    # =========================================================
    left_region = range(0, 12)  # 左边三列

    # 普通子场第一区域是 up，所以 y 从下到上
    for j in range(2*N):
        for i in left_region:
            x_local = x_list_local[i]
            y_local = y_list_local[j]

            x_global = x_offset + x_local
            y_global = y_offset + y_local

            value = gaussian_integral(x_global, y_global)

            results.append({
                "global_id": global_id,
                "subfield_id": subfield_id,
                "sub_row": sub_row + 1,
                "sub_col": sub_col + 1,
                "beam_id_in_subfield": beam_id_in_subfield,
                "region_type": "left_normal_27",
                "pattern_row": None,
                "pattern_col": None,
                "x_global": x_global,
                "y_global": y_global,
                "x_local": x_local,
                "y_local": y_local,
                "value": value
            })

            global_id += 1
            beam_id_in_subfield += 1

    # =========================================================
    # 2. 中间区域：王字形
    # =========================================================

    pattern_width_cells = 12  # 王字横向宽度 12 格 → 3 um
    bar_thick_cells = 3  # 每一横厚度 3 格 → 0.75 um
    gap_cells = 6  # 三横之间间距 6 格 → 1.5 um
    gap_cells_2 = 5  # 第二条横和第三条之间的间距 5 格 → 1.25 um
    vertical_thick_cells = 1  # 中间竖线厚度 1 格 → 0.25 um

    # 子场内部一共有多少个 0.25 um 小格
    n_cells = int(round(L_sub / cell_L))  # 9 / 0.25 = 36

    # 王字整体高度
    pattern_height_cells = 3 * bar_thick_cells + 4 * gap_cells

    # 图案左下角，使图案位于子场中心
    x0 = (n_cells - pattern_width_cells) // 2
    y0 = (n_cells - pattern_height_cells) // 2 - 1

    # 三条横的位置：bottom, middle, top
    bottom_y_start = y0
    middle_y_start = y0 + bar_thick_cells + gap_cells_2 + gap_cells + vertical_thick_cells
    top_y_start = middle_y_start + 2 * bar_thick_cells + gap_cells_2 + gap_cells + vertical_thick_cells

    # 中间竖线的位置
    vx_center = x0 + pattern_width_cells // 2
    vx_start = vx_center - vertical_thick_cells // 2
    vx_end = vx_start + vertical_thick_cells

    # 两条横的位置
    bottom_y_start_ver = y0 + bar_thick_cells + gap_cells_2
    top_y_start_ver = bottom_y_start_ver + 2 * bar_thick_cells + gap_cells_2 + gap_cells + vertical_thick_cells

    # 用 set 保存需要写入的格子，避免重复
    write_cells = set()

    # 1. 顶部横
    for yy in range(top_y_start, top_y_start + bar_thick_cells):
        for xx in range(x0, x0 + pattern_width_cells):
            write_cells.add((yy, xx))

    # 2. 中部横
    for yy in range(middle_y_start, middle_y_start + 2 * bar_thick_cells):
        for xx in range(x0, x0 + pattern_width_cells):
            write_cells.add((yy, xx))

    # 3. 底部横
    for yy in range(bottom_y_start, bottom_y_start + bar_thick_cells):
        for xx in range(x0, x0 + pattern_width_cells):
            write_cells.add((yy, xx))

    # 4. 中间竖
    for yy in range(bottom_y_start, top_y_start + bar_thick_cells):
        for xx in range(vx_start - 1, vx_end - 1):
            write_cells.add((yy, xx))

    # 5. 底部横向细线
    for yy in range(bottom_y_start_ver, bottom_y_start_ver + vertical_thick_cells):
        for xx in range(x0, x0 + pattern_width_cells):
            write_cells.add((yy, xx))

    # 6. 上部横向细线
    for yy in range(top_y_start_ver, top_y_start_ver + vertical_thick_cells):
        for xx in range(x0, x0 + pattern_width_cells):
            write_cells.add((yy, xx))

    # =====================
    # 王字形写入顺序
    # 从上到下，每一行内部从左到右
    # =====================
    ordered_cells = []

    for yy in range(n_cells - 1, -1, -1):
        row_cells = []

        for xx in range(n_cells):
            if (yy, xx) in write_cells:
                row_cells.append((yy, xx))

        if len(row_cells) > 0:
            ordered_cells.extend(row_cells)

    for yy, xx in ordered_cells:
        # 当前 0.25 um 小格的中心坐标
        x_local = (xx + 0.5) * cell_L
        y_local = (yy + 0.5) * cell_L

        x_global = x_offset + x_local
        y_global = y_offset + y_local

        value = gaussian_integral(x_global, y_global)

        results.append({
            "global_id": global_id,
            "subfield_id": subfield_id,
            "sub_row": sub_row + 1,
            "sub_col": sub_col + 1,
            "beam_id_in_subfield": beam_id_in_subfield,
            "region_type": "wang_pattern",
            "pattern_row": yy + 1,
            "pattern_col": xx + 1,
            "x_global": x_global,
            "y_global": y_global,
            "x_local": x_local,
            "y_local": y_local,
            "value": value
        })

        global_id += 1
        beam_id_in_subfield += 1

    # =========================================================
    # 3. 右边区域：27个点，和普通子场第三区域一样
    # =========================================================
    right_region = range(24, 36)  # 右边三列

    # 普通子场第三区域也是 up，所以 y 从下到上
    for j in range(2*N):
        for i in right_region:
            x_local = x_list_local[i]
            y_local = y_list_local[j]

            x_global = x_offset + x_local
            y_global = y_offset + y_local

            value = gaussian_integral(x_global, y_global)

            results.append({
                "global_id": global_id,
                "subfield_id": subfield_id,
                "sub_row": sub_row + 1,
                "sub_col": sub_col + 1,
                "beam_id_in_subfield": beam_id_in_subfield,
                "region_type": "right_normal_27",
                "pattern_row": None,
                "pattern_col": None,
                "x_global": x_global,
                "y_global": y_global,
                "x_local": x_local,
                "y_local": y_local,
                "value": value
            })

            global_id += 1
            beam_id_in_subfield += 1

    return results, global_id


# =====================
# 画第25个子场：左区域 + 王字形 + 右区域写入顺序图
# =====================
def plot_wang_pattern_order(all_results, target_subfield_id=25, save_name="wang_pattern_order_subfield25.png"):
    sub_data = [
        r for r in all_results
        if r["subfield_id"] == target_subfield_id
    ]

    if len(sub_data) == 0:
        print(f"没有找到第 {target_subfield_id} 个子场的数据")
        return

    cell_L = 0.25
    n_cells = int(round(L_sub / cell_L))

    fig, ax = plt.subplots(figsize=(10, 10))

    # 画 0.25 um 网格
    ax.set_xlim(0, L_sub)
    ax.set_ylim(0, L_sub)
    ax.set_aspect("equal")

    ax.set_xticks(np.arange(0, L_sub + cell_L, cell_L), minor=True)
    ax.set_yticks(np.arange(0, L_sub + cell_L, cell_L), minor=True)
    ax.grid(which="minor", linewidth=0.3)

    # 画 1 um 粗网格，方便看左右普通区域
    ax.set_xticks(np.arange(0, L_sub + 1, 1.0))
    ax.set_yticks(np.arange(0, L_sub + 1, 1.0))
    ax.grid(which="major", linewidth=1.0)

    # 分别画三类点
    for r in sub_data:

        x = r["x_local"]
        y = r["y_local"]
        gid = r["global_id"]

        region_type = r.get("region_type", "")

        if region_type == "left_normal_27":
            marker = "s"
            size = 120
        elif region_type == "right_normal_27":
            marker = "s"
            size = 120
        else:
            marker = "o"
            size = 45

        ax.scatter(x, y, s=size, marker=marker)

        ax.text(
            x,
            y,
            str(gid),
            ha="center",
            va="center",
            fontsize=5
        )

    # 画箭头表示整体写入顺序
    for k in range(len(sub_data) - 1):
        r1 = sub_data[k]
        r2 = sub_data[k + 1]

        x1, y1 = r1["x_local"], r1["y_local"]
        x2, y2 = r2["x_local"], r2["y_local"]

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=0.5,
                shrinkA=4,
                shrinkB=4
            )
        )

    ax.set_title("第25个子场：左27点 + 王字形 + 右27点 写入顺序")
    ax.set_xlabel("x local / um")
    ax.set_ylabel("y local / um")

    plt.tight_layout()
    plt.savefig(save_name, dpi=300)
    plt.show()

    print(f"第25个子场写入顺序图已保存：{save_name}")


# =====================
# 5x5 主场逆时针螺旋顺序
# =====================
def generate_ccw_spiral_order_from_top_right(n):
    """
    生成 n×n 主场的子场顺序。

    坐标定义：
    row = 0 表示最下方
    row = n-1 表示最上方
    col = 0 表示最左方
    col = n-1 表示最右方

    起点：最右上角，即 (row=n-1, col=n-1)
    方向：逆时针螺旋
    """

    order = []

    top = n - 1
    bottom = 0
    left = 0
    right = n - 1

    while left <= right and bottom <= top:

        # 1. 最上面一行：从右到左
        for col in range(right, left - 1, -1):
            order.append((top, col))

        top -= 1

        # 2. 最左边一列：从上到下
        for row in range(top, bottom - 1, -1):
            order.append((row, left))

        left += 1

        # 3. 最下面一行：从左到右
        if bottom <= top:
            for col in range(left, right + 1):
                order.append((bottom, col))

            bottom += 1

        # 4. 最右边一列：从下到上
        if left <= right:
            for row in range(bottom, top + 1):
                order.append((row, right))

            right -= 1

    return order


def plot_normal_subfield_order(all_results, target_subfield_id=1, save_name="normal_subfield_order_subfield1.png"):
    """
    Plot the writing order inside a normal 9x9 subfield.
    The first 24 subfields share this same internal pattern, so subfield 1 is
    enough for checking the normal write order.
    """

    sub_data = [
        r for r in all_results
        if r["subfield_id"] == target_subfield_id
    ]

    if len(sub_data) == 0:
        print(f"No data found for subfield {target_subfield_id}")
        return

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(0, L_sub)
    ax.set_ylim(0, L_sub)
    ax.set_aspect("equal")

    cell_L = 0.25
    ax.set_xticks(np.arange(0, L_sub + cell_L, cell_L), minor=True)
    ax.set_yticks(np.arange(0, L_sub + cell_L, cell_L), minor=True)
    ax.grid(which="minor", linewidth=0.3)

    ax.set_xticks(np.arange(0, L_sub + 1, 1.0))
    ax.set_yticks(np.arange(0, L_sub + 1, 1.0))
    ax.grid(True, linewidth=1.0)

    for r in sub_data:
        x = r["x_local"]
        y = r["y_local"]
        bid = r["beam_id_in_subfield"]

        ax.scatter(x, y, s=120, marker="s")
        ax.text(
            x,
            y,
            str(bid),
            ha="center",
            va="center",
            fontsize=8
        )

    for k in range(len(sub_data) - 1):
        r1 = sub_data[k]
        r2 = sub_data[k + 1]

        x1, y1 = r1["x_local"], r1["y_local"]
        x2, y2 = r2["x_local"], r2["y_local"]

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=0.8,
                shrinkA=7,
                shrinkB=7
            )
        )

    ax.set_title(f"Normal subfield {target_subfield_id}: 9x9 writing order")
    ax.set_xlabel("x local / um")
    ax.set_ylabel("y local / um")

    plt.tight_layout()
    plt.savefig(save_name, dpi=300)
    plt.show()

    print(f"Normal subfield writing order saved: {save_name}")


# =====================
# 单个子场参数
# =====================
L_sub = 9.0  # 单个子场尺寸 (um)
N = 18  # 单个子场 9x9
beam_L = 0.25  # 束斑尺寸 (um)
half_L = beam_L / 2
beta = 10.0  # 背散射半径参数 (um)
sqrt_L = L_sub / N  # 束斑中心间距 (um)

# =====================
# 主场参数
# =====================
MAIN_N = 5  # 5x5 主场
L_total = MAIN_N * L_sub  # 主场总尺寸 45 um

# 主场中心
x_center = L_total / 2 - 0.125  # 2059
y_center = L_total / 2 - 0.125  # 2059

# =====================
# 单个子场内部束斑中心
# =====================
x_list_local = np.linspace(half_L, L_sub - half_L, 2 * N)
y_list_local = np.linspace(half_L, L_sub - half_L, 2 * N)

# =====================
# 主计算
# =====================
subfield_order = generate_ccw_spiral_order_from_top_right(MAIN_N)

print("\n主场子场写入顺序：")
for idx, pos in enumerate(subfield_order, start=1):
    print(f"第 {idx:02d} 个子场: row={pos[0] + 1}, col={pos[1] + 1}")

all_results = []
global_id = 1

for subfield_id, (sub_row, sub_col) in enumerate(subfield_order, start=1):

    if subfield_id < 25:
        sub_results, global_id = generate_one_subfield(
            subfield_id=subfield_id,
            sub_row=sub_row,
            sub_col=sub_col,
            global_start_id=global_id
        )
    # 第25个子场：王字形特殊写入
    else:
        sub_results, global_id = generate_wang_pattern_subfield(
            subfield_id=subfield_id,
            sub_row=sub_row,
            sub_col=sub_col,
            global_start_id=global_id,
            cell_L=0.25,  # 每个小格子 0.25 um
        )

    all_results.extend(sub_results)

# =====================
# 输出检查
# =====================
print("总子场数量:", len(subfield_order))
print("总束斑数量:", len(all_results))

total = sum(r["value"] for r in all_results)
print("总背散射贡献:", total)

# =====================
# 选择打印某个子场的第几个束斑点
# =====================

target_subfield_id = 2  # 选择子场编号，范围 1-25
target_beam_id = 1  # 选择束斑编号，范围 1-81

found = False

for r in all_results:
    if (
            r["subfield_id"] == target_subfield_id
            and r["beam_id_in_subfield"] == target_beam_id
    ):
        print("\n找到目标束斑点：")
        print(r)
        found = True
        break

if not found:
    print("\n没有找到对应的束斑点，请检查输入编号是否正确。")

# 调用画图函数
plot_subfield_writing_order(
    subfield_order=subfield_order,
    MAIN_N=MAIN_N,
    save_name="subfield_writing_order.png"
)
# 调用画图
plot_normal_subfield_order(
    all_results=all_results,
    target_subfield_id=1,
    save_name="normal_subfield_order_subfield1.png"
)
plot_wang_pattern_order(
    all_results=all_results,
    target_subfield_id=25,
    save_name="wang_pattern_order_subfield25.png"
)

# =====================
# 导出 Excel
# =====================
df = pd.DataFrame(all_results)

file_name = "exported_results_5x5_spiral.xlsx"
df.to_excel(file_name, index=False)

print(f"\n导出成功！文件名：{file_name}")
