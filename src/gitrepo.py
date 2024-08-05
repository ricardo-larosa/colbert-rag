import os
import tempfile
from typing import List, Tuple, Dict, Set
from git import Repo, exc
import time
import hashlib
import mimetypes

class RepoCloneError(Exception):
    """Exception raised for errors in the repository cloning process."""
    pass

class FileProcessingError(Exception):
    """Exception raised for errors in processing individual files."""
    pass

def get_repo(repo_name: str, blacklist: Set[str] = set(), repo_metadata=False) -> Tuple[List[Tuple[str, str]], List[Dict[str, any]]]:
    """
    Clone a GitHub repository and read its contents, excluding files with blacklisted extensions.

    Args:
    repo_name (str): The name of the GitHub repository in the format "username/repo-name".
    blacklist (Set[str]): A set of file extensions to exclude (e.g., {'.exe', '.dll'}).

    Returns:
    Tuple[List[Tuple[str, str]], List[Dict[str, any]]]: A tuple containing file contents and metadata.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository, fetching only the default branch
        repo_url = f"https://github.com/{repo_name}.git"
        try:
            repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        except exc.GitCommandError as e:
            raise RepoCloneError(f"Failed to clone repository {repo_name}: {str(e)}")

        file_contents = []
        metadata = []

        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                _, file_extension = os.path.splitext(file)

                # Skip files with blacklisted extensions
                if file_extension.lower() in blacklist:
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    file_contents.append((relative_path, content.decode('utf-8', errors='replace')))
                    
                    file_stat = os.stat(file_path)
                    file_meta = {
                        "filename": file,
                        "path": relative_path,
                        "size_bytes": file_stat.st_size,
                        # "last_modified": time.ctime(file_stat.st_mtime),
                        # "created_time": time.ctime(file_stat.st_ctime),
                        # "file_mode": stat.filemode(file_stat.st_mode),
                        # "is_symlink": os.path.islink(file_path),
                        # "mime_type": get_mime_type(file_path),
                        "md5_hash": hashlib.md5(content).hexdigest(),
                        # "extension": file_extension,
                        # "is_executable": bool(file_stat.st_mode & stat.S_IXUSR),
                    }
                    metadata.append(file_meta)
                except Exception as e:
                    raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")

        # Add repository-level metadata
        if repo_metadata:
            repo_meta = {
                "default_branch": repo.active_branch.name,
                "commit_hash": repo.head.commit.hexsha,
                "commit_author": f"{repo.head.commit.author.name} <{repo.head.commit.author.email}>",
                "commit_message": repo.head.commit.message.strip(),
                "commit_date": time.ctime(repo.head.commit.committed_date),
            }
            metadata.append(repo_meta)

        return file_contents, metadata

def get_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


