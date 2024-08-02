import os
import tempfile
from typing import List, Tuple, Dict
from git import Repo, exc as git_exc

def clone_and_read_repo(repo_name: str) -> Tuple[List[Tuple[str, str]], List[Dict[str, str]]]:
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository
        repo_url = f"https://github.com/{repo_name}.git"
        try:
            repo = Repo.clone_from(repo_url, temp_dir)
        except git_exc.GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return [], []

        # Lists to store file contents and metadata
        file_contents = []
        metadata = []

        # Walk through the repository
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_contents.append((relative_path, content))
                    metadata.append({
                        "filename": file,
                        "path": relative_path
                    })
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    return file_contents, metadata