import sys
from main import BrainGrid2D
from container_io import save_container, container_exists, list_containers


# 容器创建
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python create_container.py <容器名称> [神经元密度]")
        print(f"已有容器: {list_containers()}")
        sys.exit(1)
    name = sys.argv[1]
    density = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0



    if container_exists(name):
        print(f"[错误] 容器 '{name}' 已存在，请使用其他名称或删除后重试")
        sys.exit(1)



    print(f"正在创建容器 '{name}' (密度={density})...")
    system = BrainGrid2D(neuron_density=density)
    system.initialize()
    neuron_count = system.get_neuron_count()
    print(f"创建完成: {neuron_count} 个活动神经元")
    save_container(system, name)
    print(f"容器已保存，可用 'python run_2d.py {name}' 启动")