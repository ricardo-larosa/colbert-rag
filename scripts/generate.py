import os
import subprocess
import glob

def protos():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proto_dir = os.path.join(root_dir, 'proto')
    output_dir = os.path.join(root_dir, 'colbert_rag', 'proto')
    
    os.makedirs(output_dir, exist_ok=True)

    proto_files = glob.glob(os.path.join(proto_dir, '*.proto'))
    
    if not proto_files:
        raise FileNotFoundError(f"No .proto files found in {proto_dir}")

    for proto_file in proto_files:
        cmd = [
            'python', '-m', 'grpc_tools.protoc',
            f'--proto_path={proto_dir}',
            f'--python_out={output_dir}',
            f'--grpc_python_out={output_dir}',
            f'--pyi_out={output_dir}',
            proto_file
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Generated Python files for {os.path.basename(proto_file)}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating files for {os.path.basename(proto_file)}: {e}")
            raise

    print(f"All proto files processed. Output directory: {output_dir}")

if __name__ == "__main__":
    generate_protos()
