import argparse
import xml.etree.ElementTree as ET
import os
import subprocess

def parse_pom(pom_file):
    """
    Парсит POM файл Maven и извлекает зависимости.
    """
    tree = ET.parse(pom_file)
    root = tree.getroot()

    namespaces = {
        'mvn': 'http://maven.apache.org/POM/4.0.0'
    }

    dependencies = []

    # Извлекаем все зависимости
    for dependency in root.findall('.//mvn:dependency', namespaces):
        group_id = dependency.find('mvn:groupId', namespaces).text
        artifact_id = dependency.find('mvn:artifactId', namespaces).text
        version = dependency.find('mvn:version', namespaces).text if dependency.find('mvn:version',
                                                                                     namespaces) is not None else 'latest'
        dependencies.append((group_id, artifact_id, version))

    return dependencies


def generate_graph(dependencies):
    """
    Генерирует код графа в формате Graphviz.
    """
    graph = "digraph G {\n"

    for group_id, artifact_id, version in dependencies:
        package_name = f"{group_id}:{artifact_id}:{version}"
        graph += f'    "{package_name}" [label="{artifact_id}"];\n'

    for i in range(len(dependencies)):
        for j in range(i + 1, len(dependencies)):
            graph += f'    "{dependencies[i][0]}:{dependencies[i][1]}:{dependencies[i][2]}" -> "{dependencies[j][0]}:{dependencies[j][1]}:{dependencies[j][2]}";\n'

    graph += "}\n"
    return graph


def generate_png(dot_file, png_file):
    """
    Конвертирует .dot файл в .png изображение с помощью Graphviz.
    """
    try:
        subprocess.run(['dot', '-Tpng', dot_file, '-o', png_file], check=True)
        print(f"Граф сохранен в PNG: {png_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации в PNG: {e}")


def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Инструмент для визуализации графа зависимостей Maven")
    parser.add_argument("pom_file", help="Путь к файлу pom.xml для анализа зависимостей Maven")
    parser.add_argument("output_file", help="Путь к файлу для сохранения кода графа (например, 'output.dot')")
    parser.add_argument("--png_file", help="Путь для сохранения графа в формате PNG (например, 'output.png')", default=None)

    args = parser.parse_args()

    # Проверка существования файла pom.xml
    if not os.path.exists(args.pom_file):
        print(f"Ошибка: файл {args.pom_file} не найден.")
        return

    # Получаем список зависимостей из POM файла
    dependencies = parse_pom(args.pom_file)

    # Генерация кода для визуализации
    graph_code = generate_graph(dependencies)

    # Сохраняем код графа в файл
    try:
        with open(args.output_file, "w") as f:
            f.write(graph_code)
        print(f"Граф зависимостей сохранен в {args.output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

    # Если указан путь для сохранения PNG, генерируем PNG изображение
    if args.png_file:
        generate_png(args.output_file, args.png_file)


if __name__ == "__main__":
    main()
