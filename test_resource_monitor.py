from modules.ResourceMonitor import ResourceMonitor


def main():
    output_dir = "output/"

    monitor = ResourceMonitor(output_dir=output_dir, interval=2)

    monitor.launch()


if __name__ == "__main__":
    main()
