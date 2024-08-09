import os
import tempfile
from typing import Any,List, Tuple, Dict, Set
from git import Repo, exc
import time
import hashlib
import mimetypes
from collections import defaultdict

class RepoCloneError(Exception):
    """Exception raised for errors in the repository cloning process."""
    pass

class FileProcessingError(Exception):
    """Exception raised for errors in processing individual files."""
    pass

def get_repo(
        repo_name: str, 
        ext_blacklist: Set[str] = set(), 
        dir_blacklist: Set[str] = set()) -> Dict[str, Tuple[List[str], List[Dict[str, Any]], List[str]]]:
    """
    Clone a GitHub repository and read its contents, excluding files with blacklisted extensions.

    Args:
    repo_name (str): The name of the GitHub repository in the format "username/repo-name".
    ext_blacklist (Set[str]): A set of file extensions to exclude (e.g., {'.exe', '.dll'}).
    dir_blacklist (Set[str]): A set of directory names to exclude (e.g., {'node_modules', 'build'}).

    Returns:
    Dict[str, Tuple[List[str], List[Dict[str, Any]], List[str]]]: A dictionary where each key is the filetype and the value is a tuple of (file_contents, metadata, ids).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository, fetching only the default branch
        repo_url = f"https://github.com/{repo_name}.git"
        try:
            repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        except exc.GitCommandError as e:
            raise RepoCloneError(f"Failed to clone repository {repo_name}: {str(e)}")

        collections = defaultdict(lambda: ([], [], []))

        for root, dirs, files in os.walk(temp_dir, topdown=True):
            # Exclude blacklisted directories only at the root level
            if root == temp_dir:
                dirs[:] = [d for d in dirs if d not in dir_blacklist]
                
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                _, file_extension = os.path.splitext(file)

                # Skip files with blacklisted extensions
                if file_extension.lower() in ext_blacklist:
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()

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
                        # determine what programming language the file is written in, based on mime type
                        "type": get_mime_type(file_path).split('/')[1] if get_mime_type(file_path).startswith("text/") else "unknown",
                        "md5_hash": hashlib.md5(content).hexdigest(),
                        "extension": file_extension,
                        # "is_executable": bool(file_stat.st_mode & stat.S_IXUSR),
                    }

                    filetype = file_meta["type"]
                    # Append data to the corresponding lists in collections
                    collections[filetype][0].append(content.decode('utf-8', errors='replace'))
                    collections[filetype][1].append(relative_path)
                    collections[filetype][2].append(file_meta)

                except Exception as e:
                    raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")

        return dict(collections) 

def get_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"
