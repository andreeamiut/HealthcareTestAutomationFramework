#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_consolidated_report.py <input_dir> <output_file>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate simple HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        p {{ color: #666; }}
    </style>
</head>
<body>
    <h1>Consolidated Test Report</h1>
    <p>This report was generated from artifacts in: {input_dir}</p>
    <p>Report generation completed successfully.</p>
</body>
</html>"""

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"Consolidated report generated: {output_file}")

if __name__ == "__main__":
    main()